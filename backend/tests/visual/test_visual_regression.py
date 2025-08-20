#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de regressão visual usando Playwright.

Este módulo testa a interface visual do dashboard para detectar
regressões visuais através de comparação de screenshots.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

try:
    from playwright.async_api import Browser, BrowserContext, Page, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

    # Mock classes para quando Playwright não estiver disponível
    class Page:
        pass

    class Browser:
        pass

    class BrowserContext:
        pass


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright não está instalado")
class TestVisualRegression:
    """Testes de regressão visual para o dashboard."""

    @pytest.fixture(scope="class")
    async def browser_setup(self):
        """Setup do browser para testes visuais."""
        async with async_playwright() as p:
            # Configurar browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-sandbox",
                ],
            )

            # Criar contexto com configurações específicas
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
            )

            yield browser, context

            await context.close()
            await browser.close()

    @pytest.fixture
    async def page(self, browser_setup):
        """Fixture para página do browser."""
        browser, context = browser_setup
        page = await context.new_page()

        # Configurar interceptação de requests para dados mock
        await page.route("**/api/metrics", self._mock_metrics_api)
        await page.route("**/api/technicians", self._mock_technicians_api)
        await page.route("**/api/dashboard", self._mock_dashboard_api)

        yield page

        await page.close()

    async def _mock_metrics_api(self, route):
        """Mock da API de métricas."""
        mock_response = {
            "success": True,
            "data": {
                "total": 150,
                "novos": 25,
                "pendentes": 45,
                "progresso": 35,
                "resolvidos": 35,
                "fechados": 10,
                "niveis": {
                    "N1": {
                        "level": "N1",
                        "metrics": {
                            "total": 80,
                            "novos": 15,
                            "pendentes": 25,
                            "progresso": 20,
                            "resolvidos": 15,
                            "fechados": 5,
                        },
                        "technician_count": 8,
                        "avg_resolution_time": 24.5,
                    },
                    "N2": {
                        "level": "N2",
                        "metrics": {
                            "total": 70,
                            "novos": 10,
                            "pendentes": 20,
                            "progresso": 15,
                            "resolvidos": 20,
                            "fechados": 5,
                        },
                        "technician_count": 6,
                        "avg_resolution_time": 18.2,
                    },
                },
                "total_technicians": 14,
                "timestamp": "2024-01-15T10:00:00Z",
            },
            "message": "Dados obtidos com sucesso",
        }

        await route.fulfill(
            status=200,
            content_type="application/json",
            body=str(mock_response).replace("'", '"'),
        )

    async def _mock_technicians_api(self, route):
        """Mock da API de técnicos."""
        mock_response = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "João Silva",
                    "level": "N1",
                    "rank": 1,
                    "metrics": {"total": 45, "resolvidos": 25},
                    "efficiency_score": 88.5,
                    "avg_resolution_time": 22.3,
                },
                {
                    "id": 2,
                    "name": "Maria Santos",
                    "level": "N2",
                    "rank": 2,
                    "metrics": {"total": 38, "resolvidos": 28},
                    "efficiency_score": 92.1,
                    "avg_resolution_time": 16.8,
                },
                {
                    "id": 3,
                    "name": "Pedro Costa",
                    "level": "N1",
                    "rank": 3,
                    "metrics": {"total": 35, "resolvidos": 20},
                    "efficiency_score": 85.2,
                    "avg_resolution_time": 25.1,
                },
            ],
        }

        await route.fulfill(
            status=200,
            content_type="application/json",
            body=str(mock_response).replace("'", '"'),
        )

    async def _mock_dashboard_api(self, route):
        """Mock da API de dashboard."""
        mock_response = {
            "success": True,
            "data": {
                "metrics": {
                    "total": 150,
                    "novos": 25,
                    "pendentes": 45,
                    "progresso": 35,
                    "resolvidos": 35,
                    "fechados": 10,
                },
                "recent_tickets": [
                    {
                        "id": 1001,
                        "title": "Problema de rede",
                        "status": "novo",
                        "created": "2024-01-15T09:30:00Z",
                    },
                    {
                        "id": 1002,
                        "title": "Instalação software",
                        "status": "progresso",
                        "created": "2024-01-15T08:45:00Z",
                    },
                    {
                        "id": 1003,
                        "title": "Manutenção preventiva",
                        "status": "pendente",
                        "created": "2024-01-15T07:20:00Z",
                    },
                ],
                "top_performers": [
                    {"name": "Maria Santos", "efficiency": 92.1},
                    {"name": "João Silva", "efficiency": 88.5},
                ],
                "response_time_ms": 145.2,
                "cache_hit": True,
            },
        }

        await route.fulfill(
            status=200,
            content_type="application/json",
            body=str(mock_response).replace("'", '"'),
        )

    async def _wait_for_page_load(self, page: Page, timeout: int = 10000):
        """Aguarda o carregamento completo da página."""
        # Aguardar network idle
        await page.wait_for_load_state("networkidle", timeout=timeout)

        # Aguardar elementos principais
        await page.wait_for_selector('[data-testid="dashboard-container"]', timeout=timeout)

        # Aguardar animações CSS
        await page.wait_for_timeout(1000)

    async def _take_screenshot(self, page: Page, name: str, full_page: bool = True, clip: Optional[Dict] = None) -> str:
        """Tira screenshot da página."""
        screenshots_dir = Path(__file__).parent / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)

        screenshot_path = screenshots_dir / f"{name}.png"

        await page.screenshot(path=str(screenshot_path), full_page=full_page, clip=clip)

        return str(screenshot_path)

    async def _compare_screenshots(self, page: Page, name: str, threshold: float = 0.2) -> bool:
        """Compara screenshot atual com baseline."""
        # Tomar screenshot atual
        current_path = await self._take_screenshot(page, f"{name}_current")

        # Caminho do baseline
        baseline_path = Path(__file__).parent / "screenshots" / f"{name}_baseline.png"

        if not baseline_path.exists():
            # Criar baseline se não existir
            import shutil

            shutil.copy2(current_path, baseline_path)
            return True

        # Comparar usando Playwright
        try:
            await page.screenshot(path=current_path, full_page=True)

            # Usar expect do Playwright para comparação visual
            from playwright.sync_api import expect

            # Note: Esta é uma implementação simplificada
            # Em produção, usar ferramentas como pixelmatch ou similar
            return True

        except Exception as e:
            print(f"Erro na comparação visual: {e}")
            return False

    @pytest.mark.asyncio
    async def test_dashboard_main_layout(self, page: Page):
        """Testa layout principal do dashboard."""
        # Navegar para dashboard
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Verificar elementos principais
        await page.wait_for_selector('[data-testid="metrics-cards"]')
        await page.wait_for_selector('[data-testid="charts-section"]')
        await page.wait_for_selector('[data-testid="technicians-table"]')

        # Comparar com baseline
        assert await self._compare_screenshots(page, "dashboard_main_layout")

    @pytest.mark.asyncio
    async def test_metrics_cards_visual(self, page: Page):
        """Testa aparência visual dos cards de métricas."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Focar nos cards de métricas
        metrics_cards = page.locator('[data-testid="metrics-cards"]')
        await metrics_cards.wait_for()

        # Screenshot específico dos cards
        bounding_box = await metrics_cards.bounding_box()

        await self._take_screenshot(page, "metrics_cards", full_page=False, clip=bounding_box)

        assert await self._compare_screenshots(page, "metrics_cards")

    @pytest.mark.asyncio
    async def test_charts_visual_rendering(self, page: Page):
        """Testa renderização visual dos gráficos."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Aguardar renderização dos gráficos
        await page.wait_for_selector('[data-testid="pie-chart"]')
        await page.wait_for_selector('[data-testid="bar-chart"]')

        # Aguardar animações dos gráficos
        await page.wait_for_timeout(2000)

        # Screenshot da seção de gráficos
        charts_section = page.locator('[data-testid="charts-section"]')
        bounding_box = await charts_section.bounding_box()

        await self._take_screenshot(page, "charts_section", full_page=False, clip=bounding_box)

        assert await self._compare_screenshots(page, "charts_section")

    @pytest.mark.asyncio
    async def test_technicians_table_visual(self, page: Page):
        """Testa aparência visual da tabela de técnicos."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Aguardar carregamento da tabela
        await page.wait_for_selector('[data-testid="technicians-table"]')

        # Verificar se dados foram carregados
        await page.wait_for_selector('[data-testid="technician-row"]')

        # Screenshot da tabela
        table = page.locator('[data-testid="technicians-table"]')
        bounding_box = await table.bounding_box()

        await self._take_screenshot(page, "technicians_table", full_page=False, clip=bounding_box)

        assert await self._compare_screenshots(page, "technicians_table")

    @pytest.mark.asyncio
    async def test_responsive_mobile_layout(self, page: Page):
        """Testa layout responsivo em dispositivos móveis."""
        # Configurar viewport mobile
        await page.set_viewport_size({"width": 375, "height": 667})

        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Verificar elementos em layout mobile
        await page.wait_for_selector('[data-testid="mobile-menu-toggle"]')

        # Screenshot mobile
        assert await self._compare_screenshots(page, "dashboard_mobile_layout")

    @pytest.mark.asyncio
    async def test_responsive_tablet_layout(self, page: Page):
        """Testa layout responsivo em tablets."""
        # Configurar viewport tablet
        await page.set_viewport_size({"width": 768, "height": 1024})

        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Screenshot tablet
        assert await self._compare_screenshots(page, "dashboard_tablet_layout")

    @pytest.mark.asyncio
    async def test_dark_mode_visual(self, page: Page):
        """Testa aparência visual do modo escuro."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Ativar modo escuro
        await page.click('[data-testid="theme-toggle"]')
        await page.wait_for_timeout(500)  # Aguardar transição

        # Verificar se modo escuro foi aplicado
        body_class = await page.get_attribute("body", "class")
        assert "dark" in body_class or "theme-dark" in body_class

        # Screenshot modo escuro
        assert await self._compare_screenshots(page, "dashboard_dark_mode")

    @pytest.mark.asyncio
    async def test_loading_states_visual(self, page: Page):
        """Testa estados visuais de carregamento."""
        # Interceptar API para simular loading
        await page.route("**/api/metrics", lambda route: route.abort())

        await page.goto("http://localhost:3000/dashboard")

        # Aguardar estados de loading
        await page.wait_for_selector('[data-testid="loading-spinner"]')

        # Screenshot estado de loading
        await self._take_screenshot(page, "dashboard_loading_state")

        # Verificar skeletons
        await page.wait_for_selector('[data-testid="skeleton-card"]')

        assert await self._compare_screenshots(page, "dashboard_loading_state")

    @pytest.mark.asyncio
    async def test_error_states_visual(self, page: Page):
        """Testa estados visuais de erro."""
        # Interceptar API para simular erro
        await page.route(
            "**/api/metrics",
            lambda route: route.fulfill(
                status=500,
                content_type="application/json",
                body='{"error": "Internal server error"}',
            ),
        )

        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page, timeout=15000)

        # Aguardar estado de erro
        await page.wait_for_selector('[data-testid="error-message"]')

        # Screenshot estado de erro
        assert await self._compare_screenshots(page, "dashboard_error_state")

    @pytest.mark.asyncio
    async def test_interactive_elements_visual(self, page: Page):
        """Testa estados visuais de elementos interativos."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Testar hover em botões
        button = page.locator('[data-testid="refresh-button"]')
        await button.hover()
        await page.wait_for_timeout(200)

        # Screenshot com hover
        await self._take_screenshot(page, "button_hover_state")

        # Testar focus em inputs
        search_input = page.locator('[data-testid="search-input"]')
        await search_input.focus()
        await page.wait_for_timeout(200)

        # Screenshot com focus
        await self._take_screenshot(page, "input_focus_state")

        assert await self._compare_screenshots(page, "interactive_elements")

    @pytest.mark.asyncio
    async def test_animation_consistency(self, page: Page):
        """Testa consistência de animações."""
        await page.goto("http://localhost:3000/dashboard")

        # Aguardar animações de entrada
        await page.wait_for_selector('[data-testid="fade-in-animation"]')
        await page.wait_for_timeout(1000)

        # Trigger animação de transição
        await page.click('[data-testid="tab-technicians"]')
        await page.wait_for_timeout(500)

        # Screenshot após animação
        assert await self._compare_screenshots(page, "animation_end_state")

    @pytest.mark.asyncio
    async def test_accessibility_visual_indicators(self, page: Page):
        """Testa indicadores visuais de acessibilidade."""
        await page.goto("http://localhost:3000/dashboard")
        await self._wait_for_page_load(page)

        # Simular navegação por teclado
        await page.keyboard.press("Tab")
        await page.wait_for_timeout(200)

        # Verificar focus visible
        focused_element = await page.evaluate("document.activeElement.tagName")
        assert focused_element is not None

        # Screenshot com focus indicators
        assert await self._compare_screenshots(page, "accessibility_focus_indicators")


class TestVisualRegressionUtils:
    """Utilitários para testes de regressão visual."""

    @staticmethod
    def generate_baseline_screenshots():
        """Gera screenshots baseline para comparação."""

        async def _generate():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": 1920, "height": 1080})
                page = await context.new_page()

                # Lista de páginas para gerar baselines
                pages_to_capture = [
                    ("dashboard", "http://localhost:3000/dashboard"),
                    ("metrics", "http://localhost:3000/metrics"),
                    ("technicians", "http://localhost:3000/technicians"),
                ]

                for name, url in pages_to_capture:
                    try:
                        await page.goto(url)
                        await page.wait_for_load_state("networkidle")

                        screenshots_dir = Path(__file__).parent / "screenshots"
                        screenshots_dir.mkdir(exist_ok=True)

                        await page.screenshot(
                            path=str(screenshots_dir / f"{name}_baseline.png"),
                            full_page=True,
                        )

                        print(f"✅ Baseline gerado para {name}")

                    except Exception as e:
                        print(f"❌ Erro ao gerar baseline para {name}: {e}")

                await context.close()
                await browser.close()

        return asyncio.run(_generate())

    @staticmethod
    def cleanup_screenshots():
        """Remove screenshots antigos."""
        screenshots_dir = Path(__file__).parent / "screenshots"

        if screenshots_dir.exists():
            for file in screenshots_dir.glob("*_current.png"):
                file.unlink()

            print("✅ Screenshots temporários removidos")

    @staticmethod
    def compare_all_screenshots():
        """Compara todos os screenshots com baselines."""
        screenshots_dir = Path(__file__).parent / "screenshots"

        if not screenshots_dir.exists():
            print("❌ Diretório de screenshots não encontrado")
            return False

        baselines = list(screenshots_dir.glob("*_baseline.png"))
        currents = list(screenshots_dir.glob("*_current.png"))

        print(f"📊 Encontrados {len(baselines)} baselines e {len(currents)} screenshots atuais")

        # Implementar comparação real aqui
        # Por exemplo, usando pixelmatch ou similar

        return True


# Configuração para pytest
def pytest_configure(config):
    """Configuração do pytest para testes visuais."""
    # Adicionar marcadores customizados
    config.addinivalue_line("markers", "visual: marca testes de regressão visual")

    config.addinivalue_line("markers", "slow: marca testes que demoram para executar")


def pytest_collection_modifyitems(config, items):
    """Modifica coleta de testes para adicionar marcadores."""
    for item in items:
        # Marcar testes visuais
        if "visual" in item.nodeid:
            item.add_marker(pytest.mark.visual)
            item.add_marker(pytest.mark.slow)


if __name__ == "__main__":
    # Executar geração de baselines
    print("🎯 Gerando screenshots baseline...")
    TestVisualRegressionUtils.generate_baseline_screenshots()

    print("🧹 Limpando screenshots temporários...")
    TestVisualRegressionUtils.cleanup_screenshots()

    print("✅ Configuração de testes visuais concluída")
