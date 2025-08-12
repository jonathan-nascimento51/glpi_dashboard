import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from models.validation import (
    TicketStatus,
    Priority,
    TechnicianLevel,
    LevelMetrics,
    MetricsData,
    TechnicianRanking,
    Ticket,
    NewTicket,
    SystemStatus,
    FilterParams,
    ApiResponse,
)


class TestTicketStatus:
    """Testes para enum TicketStatus"""

    def test_valid_status_values(self):
        """Testa valores válidos de status"""
        assert TicketStatus.ABERTO == "aberto"
        assert TicketStatus.EM_ANDAMENTO == "em_andamento"
        assert TicketStatus.RESOLVIDO == "resolvido"

    def test_invalid_status_raises_error(self):
        """Testa que valores inválidos geram erro"""
        with pytest.raises(ValueError):
            TicketStatus("status_invalido")


class TestLevelMetrics:
    """Testes para modelo LevelMetrics"""

    def test_valid_level_metrics(self):
        """Testa criação válida de métricas de nível"""
        metrics = LevelMetrics(total=100, resolvidos=80, pendentes=20, tempo_medio=2.5)
        assert metrics.total == 100
        assert metrics.resolvidos == 80
        assert metrics.pendentes == 20
        assert metrics.tempo_medio == 2.5

    def test_resolvidos_greater_than_total_raises_error(self):
        """Testa que resolvidos > total gera erro"""
        with pytest.raises(ValidationError) as exc_info:
            LevelMetrics(total=50, resolvidos=60, pendentes=0, tempo_medio=1.0)
        assert "Resolvidos não pode ser maior que total" in str(exc_info.value)

    def test_inconsistent_pendentes_raises_error(self):
        """Testa que pendentes inconsistente gera erro"""
        with pytest.raises(ValidationError) as exc_info:
            LevelMetrics(
                total=100,
                resolvidos=80,
                pendentes=30,  # Deveria ser 20
                tempo_medio=1.0,
            )
        assert "Pendentes deve ser" in str(exc_info.value)

    def test_negative_values_raise_error(self):
        """Testa que valores negativos geram erro"""
        with pytest.raises(ValidationError):
            LevelMetrics(total=-1, resolvidos=0, pendentes=0, tempo_medio=1.0)

        with pytest.raises(ValidationError):
            LevelMetrics(total=10, resolvidos=5, pendentes=5, tempo_medio=-1.0)


class TestMetricsData:
    """Testes para modelo MetricsData"""

    def test_valid_metrics_data(self):
        """Testa criação válida de dados de métricas"""
        metrics = MetricsData(
            niveis={
                TechnicianLevel.N1: LevelMetrics(
                    total=50, resolvidos=40, pendentes=10, tempo_medio=1.5
                ),
                TechnicianLevel.N2: LevelMetrics(
                    total=30, resolvidos=25, pendentes=5, tempo_medio=2.0
                ),
            },
            total_tickets=80,
            tickets_resolvidos=65,
            tickets_pendentes=15,
            tempo_medio_resolucao=1.7,
            satisfacao_cliente=4.2,
        )
        assert metrics.total_tickets == 80
        assert metrics.satisfacao_cliente == 4.2

    def test_inconsistent_totals_raise_error(self):
        """Testa que totais inconsistentes geram erro"""
        with pytest.raises(ValidationError) as exc_info:
            MetricsData(
                niveis={
                    TechnicianLevel.N1: LevelMetrics(
                        total=50, resolvidos=40, pendentes=10, tempo_medio=1.5
                    )
                },
                total_tickets=100,  # Inconsistente com níveis (50)
                tickets_resolvidos=40,
                tickets_pendentes=10,
                tempo_medio_resolucao=1.5,
                satisfacao_cliente=4.0,
            )
        assert "Total de tickets inconsistente" in str(exc_info.value)

    def test_satisfacao_out_of_range_raises_error(self):
        """Testa que satisfação fora do range gera erro"""
        with pytest.raises(ValidationError):
            MetricsData(
                niveis={},
                total_tickets=0,
                tickets_resolvidos=0,
                tickets_pendentes=0,
                tempo_medio_resolucao=1.0,
                satisfacao_cliente=6.0,  # Fora do range 0-5
            )


class TestTechnicianRanking:
    """Testes para modelo TechnicianRanking"""

    def test_valid_technician_ranking(self):
        """Testa criação válida de ranking de técnico"""
        ranking = TechnicianRanking(
            id=1,
            nome="João Silva",
            tickets_resolvidos=50,
            tempo_medio=2.5,
            satisfacao=4.8,
            nivel=TechnicianLevel.N2,
        )
        assert ranking.nome == "João Silva"
        assert ranking.nivel == TechnicianLevel.N2

    def test_nome_is_title_cased(self):
        """Testa que nome é convertido para title case"""
        ranking = TechnicianRanking(
            id=1,
            nome="joão silva",
            tickets_resolvidos=10,
            tempo_medio=1.0,
            satisfacao=4.0,
            nivel=TechnicianLevel.N1,
        )
        assert ranking.nome == "João Silva"

    def test_empty_nome_raises_error(self):
        """Testa que nome vazio gera erro"""
        with pytest.raises(ValidationError) as exc_info:
            TechnicianRanking(
                id=1,
                nome="   ",  # Nome vazio
                tickets_resolvidos=10,
                tempo_medio=1.0,
                satisfacao=4.0,
                nivel=TechnicianLevel.N1,
            )
        assert "Nome não pode estar vazio" in str(exc_info.value)

    def test_invalid_id_raises_error(self):
        """Testa que ID inválido gera erro"""
        with pytest.raises(ValidationError):
            TechnicianRanking(
                id=0,  # ID deve ser positivo
                nome="João",
                tickets_resolvidos=10,
                tempo_medio=1.0,
                satisfacao=4.0,
                nivel=TechnicianLevel.N1,
            )


class TestTicket:
    """Testes para modelo Ticket"""

    def test_valid_ticket(self):
        """Testa criação válida de ticket"""
        now = datetime.now()
        ticket = Ticket(
            id=1,
            titulo="Problema no sistema",
            descricao="Descrição detalhada do problema",
            status=TicketStatus.ABERTO,
            prioridade=Priority.ALTA,
            categoria="Hardware",
            solicitante="Maria Santos",
            data_abertura=now,
        )
        assert ticket.titulo == "Problema no sistema"
        assert ticket.status == TicketStatus.ABERTO

    def test_data_fechamento_before_abertura_raises_error(self):
        """Testa que data de fechamento anterior à abertura gera erro"""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            Ticket(
                id=1,
                titulo="Teste",
                descricao="Descrição teste",
                status=TicketStatus.FECHADO,
                prioridade=Priority.NORMAL,
                categoria="Software",
                solicitante="Teste",
                data_abertura=now,
                data_fechamento=now - timedelta(hours=1),  # Anterior à abertura
            )
        assert "Data de fechamento não pode ser anterior" in str(exc_info.value)

    def test_resolved_ticket_requires_fechamento_and_tempo(self):
        """Testa que ticket resolvido requer data de fechamento e tempo"""
        now = datetime.now()

        # Sem data de fechamento
        with pytest.raises(ValidationError) as exc_info:
            Ticket(
                id=1,
                titulo="Teste resolvido",
                descricao="Descrição teste",
                status=TicketStatus.RESOLVIDO,
                prioridade=Priority.NORMAL,
                categoria="Software",
                solicitante="Teste",
                data_abertura=now,
                # Faltando data_fechamento e tempo_resolucao
            )
        assert "devem ter data de fechamento" in str(exc_info.value)

    def test_titulo_too_short_raises_error(self):
        """Testa que título muito curto gera erro"""
        with pytest.raises(ValidationError):
            Ticket(
                id=1,
                titulo="ABC",  # Muito curto (min 5)
                descricao="Descrição válida",
                status=TicketStatus.ABERTO,
                prioridade=Priority.NORMAL,
                categoria="Software",
                solicitante="Teste",
                data_abertura=datetime.now(),
            )


class TestSystemStatus:
    """Testes para modelo SystemStatus"""

    def test_valid_system_status(self):
        """Testa criação válida de status do sistema"""
        status = SystemStatus(
            api_status="healthy",
            database_status="healthy",
            glpi_connection="healthy",
            response_time=150.0,
            uptime=3600.0,
            version="1.0.0",
        )
        assert status.api_status == "healthy"
        assert status.response_time == 150.0

    def test_invalid_status_values_raise_error(self):
        """Testa que valores de status inválidos geram erro"""
        with pytest.raises(ValidationError):
            SystemStatus(
                api_status="invalid_status",  # Deve ser healthy/degraded/unhealthy
                database_status="healthy",
                glpi_connection="healthy",
                response_time=150.0,
                uptime=3600.0,
                version="1.0.0",
            )

    def test_response_time_too_high_raises_error(self):
        """Testa que tempo de resposta muito alto gera erro"""
        with pytest.raises(ValidationError) as exc_info:
            SystemStatus(
                api_status="healthy",
                database_status="healthy",
                glpi_connection="healthy",
                response_time=35000.0,  # Maior que 30000ms
                uptime=3600.0,
                version="1.0.0",
            )
        assert "Tempo de resposta muito alto" in str(exc_info.value)


class TestFilterParams:
    """Testes para modelo FilterParams"""

    def test_valid_filter_params(self):
        """Testa criação válida de parâmetros de filtro"""
        now = datetime.now()
        filters = FilterParams(
            status=[TicketStatus.ABERTO, TicketStatus.EM_ANDAMENTO],
            prioridade=[Priority.ALTA],
            categoria="Hardware",
            data_inicio=now - timedelta(days=7),
            data_fim=now,
            limite=100,
        )
        assert len(filters.status) == 2
        assert filters.limite == 100

    def test_data_fim_before_inicio_raises_error(self):
        """Testa que data fim anterior ao início gera erro"""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            FilterParams(
                data_inicio=now,
                data_fim=now - timedelta(days=1),  # Anterior ao início
            )
        assert "Data fim não pode ser anterior" in str(exc_info.value)

    def test_limite_out_of_range_raises_error(self):
        """Testa que limite fora do range gera erro"""
        with pytest.raises(ValidationError):
            FilterParams(limite=0)  # Menor que 1

        with pytest.raises(ValidationError):
            FilterParams(limite=1001)  # Maior que 1000


class TestApiResponse:
    """Testes para modelo ApiResponse"""

    def test_valid_api_response(self):
        """Testa criação válida de resposta da API"""
        response = ApiResponse(
            success=True,
            message="Operação realizada com sucesso",
            data={"result": "ok"},
        )
        assert response.success is True
        assert "sucesso" in response.message

    def test_empty_message_raises_error(self):
        """Testa que mensagem vazia gera erro"""
        with pytest.raises(ValidationError) as exc_info:
            ApiResponse(
                success=True,
                message="   ",  # Mensagem vazia
            )
        assert "Mensagem não pode estar vazia" in str(exc_info.value)

    def test_message_is_stripped(self):
        """Testa que mensagem é limpa de espaços"""
        response = ApiResponse(success=True, message="  Mensagem com espaços  ")
        assert response.message == "Mensagem com espaços"


class TestNewTicket:
    """Testes para modelo NewTicket"""

    def test_valid_new_ticket(self):
        """Testa criação válida de novo ticket"""
        ticket = NewTicket(
            titulo="Novo problema",
            descricao="Descrição detalhada",
            prioridade=Priority.NORMAL,
            categoria="Software",
            solicitante="João Silva",
        )
        assert ticket.titulo == "Novo problema"
        assert ticket.prioridade == Priority.NORMAL

    def test_fields_are_stripped(self):
        """Testa que campos são limpos de espaços"""
        ticket = NewTicket(
            titulo="  Título com espaços  ",
            descricao="  Descrição com espaços  ",
            prioridade=Priority.NORMAL,
            categoria="  Categoria  ",
            solicitante="  Solicitante  ",
        )
        assert ticket.titulo == "Título com espaços"
        assert ticket.categoria == "Categoria"

    def test_empty_fields_raise_error(self):
        """Testa que campos vazios geram erro"""
        with pytest.raises(ValidationError):
            NewTicket(
                titulo="   ",  # Vazio
                descricao="Descrição válida",
                prioridade=Priority.NORMAL,
                categoria="Software",
                solicitante="João",
            )
