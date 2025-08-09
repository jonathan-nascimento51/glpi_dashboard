import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
import psutil
import os

from main import app


class TestLoadTesting:
    """Testes de carga para a API."""

    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
        self.base_url = "/api"
        self.process = psutil.Process(os.getpid())

    def get_system_metrics(self):
        """Obtém métricas do sistema."""
        return {
            "cpu_percent": self.process.cpu_percent(),
            "memory_mb": self.process.memory_info().rss / 1024 / 1024,
            "threads": self.process.num_threads(),
        }

    def test_light_load_100_requests(self, mock_glpi_service):
        """Testa carga leve com 100 requisições sequenciais."""
        num_requests = 100
        response_times = []
        errors = 0

        start_time = time.time()

        for i in range(num_requests):
            request_start = time.time()

            try:
                response = self.client.get(f"{self.base_url}/dashboard/metrics")
                request_end = time.time()

                response_times.append(request_end - request_start)

                if response.status_code != 200:
                    errors += 1

            except Exception as e:
                errors += 1
                print(f"Request {i} failed: {e}")

        total_time = time.time() - start_time

        # Análise dos resultados
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[
            18
        ]  # 95th percentile

        # Verificações
        assert errors == 0, f"Houve {errors} erros durante o teste"
        assert (
            avg_response_time < 1.0
        ), f"Tempo médio de resposta muito alto: {avg_response_time:.2f}s"
        assert (
            max_response_time < 3.0
        ), f"Tempo máximo de resposta muito alto: {max_response_time:.2f}s"
        assert (
            p95_response_time < 2.0
        ), f"95º percentil muito alto: {p95_response_time:.2f}s"

        print("\n📊 Resultados do teste de carga leve:")
        print(f"   Total de requisições: {num_requests}")
        print(f"   Tempo total: {total_time:.2f}s")
        print(f"   Requisições por segundo: {num_requests / total_time:.2f}")
        print(f"   Tempo médio de resposta: {avg_response_time:.3f}s")
        print(f"   Tempo mínimo: {min_response_time:.3f}s")
        print(f"   Tempo máximo: {max_response_time:.3f}s")
        print(f"   95º percentil: {p95_response_time:.3f}s")

    def test_medium_load_concurrent_requests(self, mock_glpi_service):
        """Testa carga média com requisições concorrentes."""
        num_requests = 50
        max_workers = 10

        def make_request(request_id):
            start_time = time.time()
            try:
                response = self.client.get(f"{self.base_url}/dashboard/metrics")
                end_time = time.time()

                return {
                    "id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                    "error": None,
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "id": request_id,
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e),
                }

        # Métricas do sistema antes do teste
        initial_metrics = self.get_system_metrics()

        start_time = time.time()

        # Executar requisições concorrentes
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time

        # Métricas do sistema após o teste
        final_metrics = self.get_system_metrics()

        # Análise dos resultados
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        response_times = [r["response_time"] for r in successful_requests]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) > 20
                else max_response_time
            )
        else:
            avg_response_time = max_response_time = p95_response_time = 0

        # Verificações
        success_rate = len(successful_requests) / num_requests
        assert success_rate >= 0.95, f"Taxa de sucesso muito baixa: {success_rate:.2%}"

        if response_times:
            assert (
                avg_response_time < 2.0
            ), f"Tempo médio de resposta muito alto: {avg_response_time:.2f}s"
            assert (
                max_response_time < 5.0
            ), f"Tempo máximo de resposta muito alto: {max_response_time:.2f}s"

        # Verificar uso de recursos
        memory_increase = final_metrics["memory_mb"] - initial_metrics["memory_mb"]
        assert (
            memory_increase < 100
        ), f"Aumento de memória muito alto: {memory_increase:.2f}MB"

        print("\n📊 Resultados do teste de carga média:")
        print(f"   Total de requisições: {num_requests}")
        print(f"   Workers concorrentes: {max_workers}")
        print(f"   Tempo total: {total_time:.2f}s")
        print(f"   Requisições por segundo: {num_requests / total_time:.2f}")
        print(f"   Taxa de sucesso: {success_rate:.2%}")
        print(f"   Requisições falharam: {len(failed_requests)}")
        if response_times:
            print(f"   Tempo médio de resposta: {avg_response_time:.3f}s")
            print(f"   Tempo máximo: {max_response_time:.3f}s")
            print(f"   95º percentil: {p95_response_time:.3f}s")
        print(f"   Uso de memória inicial: {initial_metrics['memory_mb']:.2f}MB")
        print(f"   Uso de memória final: {final_metrics['memory_mb']:.2f}MB")
        print(f"   Aumento de memória: {memory_increase:.2f}MB")

    def test_heavy_load_stress_test(self, mock_glpi_service):
        """Testa carga pesada para identificar limites."""
        num_requests = 200
        max_workers = 20

        def make_request(request_id):
            start_time = time.time()
            try:
                response = self.client.get(f"{self.base_url}/dashboard/metrics")
                end_time = time.time()

                return {
                    "id": request_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                    "timestamp": start_time,
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "id": request_id,
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "timestamp": start_time,
                    "error": str(e),
                }

        # Monitorar métricas do sistema durante o teste
        system_metrics = []

        def monitor_system():
            while not stop_monitoring.is_set():
                metrics = self.get_system_metrics()
                metrics["timestamp"] = time.time()
                system_metrics.append(metrics)
                time.sleep(0.5)

        stop_monitoring = threading.Event()
        monitor_thread = threading.Thread(target=monitor_system)
        monitor_thread.start()

        try:
            start_time = time.time()

            # Executar requisições concorrentes
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(make_request, i) for i in range(num_requests)
                ]
                results = [future.result() for future in as_completed(futures)]

            total_time = time.time() - start_time

        finally:
            stop_monitoring.set()
            monitor_thread.join()

        # Análise dos resultados
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        response_times = [r["response_time"] for r in successful_requests]

        # Análise temporal (requisições por segundo ao longo do tempo)
        time_buckets = {}
        for result in results:
            bucket = int(result["timestamp"] - start_time)
            if bucket not in time_buckets:
                time_buckets[bucket] = []
            time_buckets[bucket].append(result)

        # Verificações (mais flexíveis para teste de stress)
        success_rate = len(successful_requests) / num_requests
        assert (
            success_rate >= 0.80
        ), f"Taxa de sucesso muito baixa para teste de stress: {success_rate:.2%}"

        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)

            # Limites mais flexíveis para teste de stress
            assert (
                avg_response_time < 5.0
            ), f"Tempo médio de resposta extremamente alto: {avg_response_time:.2f}s"
            assert (
                max_response_time < 10.0
            ), f"Tempo máximo de resposta extremamente alto: {max_response_time:.2f}s"

        # Análise de métricas do sistema
        if system_metrics:
            max_memory = max(m["memory_mb"] for m in system_metrics)
            max_cpu = max(m["cpu_percent"] for m in system_metrics)

            print("\n📊 Resultados do teste de stress:")
            print(f"   Total de requisições: {num_requests}")
            print(f"   Workers concorrentes: {max_workers}")
            print(f"   Tempo total: {total_time:.2f}s")
            print(f"   Requisições por segundo: {num_requests / total_time:.2f}")
            print(f"   Taxa de sucesso: {success_rate:.2%}")
            print(f"   Requisições falharam: {len(failed_requests)}")

            if response_times:
                print(
                    f"   Tempo médio de resposta: {statistics.mean(response_times):.3f}s"
                )
                print(f"   Tempo máximo: {max(response_times):.3f}s")
                print(f"   Tempo mínimo: {min(response_times):.3f}s")

                if len(response_times) > 10:
                    p95 = statistics.quantiles(response_times, n=20)[18]
                    p99 = statistics.quantiles(response_times, n=100)[98]
                    print(f"   95º percentil: {p95:.3f}s")
                    print(f"   99º percentil: {p99:.3f}s")

            print(f"   Pico de memória: {max_memory:.2f}MB")
            print(f"   Pico de CPU: {max_cpu:.1f}%")

    def test_sustained_load_endurance(self, mock_glpi_service):
        """Testa carga sustentada por um período prolongado."""
        duration_seconds = 30  # 30 segundos de teste
        requests_per_second = 5

        results = []
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration_seconds:
            batch_start = time.time()

            # Fazer requisições para atingir a taxa desejada
            for _ in range(requests_per_second):
                request_start = time.time()

                try:
                    response = self.client.get(f"{self.base_url}/dashboard/metrics")
                    request_end = time.time()

                    results.append(
                        {
                            "request_id": request_count,
                            "status_code": response.status_code,
                            "response_time": request_end - request_start,
                            "success": response.status_code == 200,
                            "timestamp": request_start - start_time,
                        }
                    )

                except Exception as e:
                    request_end = time.time()
                    results.append(
                        {
                            "request_id": request_count,
                            "status_code": 0,
                            "response_time": request_end - request_start,
                            "success": False,
                            "timestamp": request_start - start_time,
                            "error": str(e),
                        }
                    )

                request_count += 1

            # Aguardar para manter a taxa de requisições
            batch_duration = time.time() - batch_start
            sleep_time = max(0, 1.0 - batch_duration)
            if sleep_time > 0:
                time.sleep(sleep_time)

        total_time = time.time() - start_time

        # Análise dos resultados
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        response_times = [r["response_time"] for r in successful_requests]

        # Análise de degradação ao longo do tempo
        time_windows = {}
        window_size = 5  # janelas de 5 segundos

        for result in results:
            window = int(result["timestamp"] // window_size)
            if window not in time_windows:
                time_windows[window] = []
            time_windows[window].append(result)

        # Verificar se a performance se mantém estável
        window_avg_times = []
        for window_results in time_windows.values():
            window_successful = [r for r in window_results if r["success"]]
            if window_successful:
                window_response_times = [r["response_time"] for r in window_successful]
                window_avg_times.append(statistics.mean(window_response_times))

        # Verificações
        success_rate = len(successful_requests) / len(results)
        assert (
            success_rate >= 0.95
        ), f"Taxa de sucesso degradou durante teste prolongado: {success_rate:.2%}"

        if response_times:
            overall_avg = statistics.mean(response_times)
            assert (
                overall_avg < 2.0
            ), f"Tempo médio de resposta degradou: {overall_avg:.2f}s"

        # Verificar estabilidade (variação entre janelas de tempo)
        if len(window_avg_times) > 1:
            time_variance = statistics.variance(window_avg_times)
            assert (
                time_variance < 1.0
            ), f"Performance muito instável ao longo do tempo: {time_variance:.3f}"

        print("\n📊 Resultados do teste de resistência:")
        print(f"   Duração: {total_time:.1f}s")
        print(f"   Total de requisições: {len(results)}")
        print(f"   Taxa alvo: {requests_per_second} req/s")
        print(f"   Taxa real: {len(results) / total_time:.2f} req/s")
        print(f"   Taxa de sucesso: {success_rate:.2%}")

        if response_times:
            print(f"   Tempo médio de resposta: {statistics.mean(response_times):.3f}s")
            print(f"   Desvio padrão: {statistics.stdev(response_times):.3f}s")

        if window_avg_times:
            print(f"   Janelas de tempo analisadas: {len(window_avg_times)}")
            print(
                f"   Variância entre janelas: {statistics.variance(window_avg_times):.3f}"
            )

    def test_memory_leak_detection(self, mock_glpi_service):
        """Testa se há vazamentos de memória."""
        num_iterations = 10
        requests_per_iteration = 20

        memory_measurements = []

        for iteration in range(num_iterations):
            # Medir memória antes da iteração
            initial_memory = self.get_system_metrics()["memory_mb"]

            # Fazer várias requisições
            for _ in range(requests_per_iteration):
                response = self.client.get(f"{self.base_url}/dashboard/metrics")
                assert response.status_code == 200

            # Forçar garbage collection
            import gc

            gc.collect()

            # Medir memória após a iteração
            final_memory = self.get_system_metrics()["memory_mb"]

            memory_measurements.append(
                {
                    "iteration": iteration,
                    "initial_memory": initial_memory,
                    "final_memory": final_memory,
                    "memory_increase": final_memory - initial_memory,
                }
            )

            # Pequena pausa entre iterações
            time.sleep(0.1)

        # Análise de vazamento de memória
        memory_increases = [m["memory_increase"] for m in memory_measurements]
        total_memory_increase = sum(memory_increases)
        avg_memory_increase = statistics.mean(memory_increases)

        # Verificações
        assert (
            total_memory_increase < 50
        ), f"Possível vazamento de memória: {total_memory_increase:.2f}MB de aumento total"
        assert (
            avg_memory_increase < 5
        ), f"Aumento médio de memória muito alto: {avg_memory_increase:.2f}MB por iteração"

        # Verificar tendência crescente
        first_half = memory_increases[: num_iterations // 2]
        second_half = memory_increases[num_iterations // 2 :]

        if first_half and second_half:
            first_half_avg = statistics.mean(first_half)
            second_half_avg = statistics.mean(second_half)

            # A segunda metade não deve ter aumento significativamente maior
            assert (
                second_half_avg <= first_half_avg * 2
            ), "Possível vazamento de memória detectado"

        print("\n📊 Resultados do teste de vazamento de memória:")
        print(f"   Iterações: {num_iterations}")
        print(f"   Requisições por iteração: {requests_per_iteration}")
        print(f"   Aumento total de memória: {total_memory_increase:.2f}MB")
        print(f"   Aumento médio por iteração: {avg_memory_increase:.2f}MB")
        print(f"   Maior aumento em uma iteração: {max(memory_increases):.2f}MB")
        print(f"   Menor aumento em uma iteração: {min(memory_increases):.2f}MB")
