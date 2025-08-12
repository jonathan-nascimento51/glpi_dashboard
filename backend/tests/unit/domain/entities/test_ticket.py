import pytest
from datetime import datetime, timezone
from domain.entities.ticket import Ticket, TicketStatus, TicketPriority
from tests.factories import TicketFactory, ResolvedTicketFactory


class TestTicket:
    """Testes para a entidade Ticket."""

    def test_create_ticket_manually(self):
        """Testa criação manual de um ticket."""
        now = datetime.now(timezone.utc)
        ticket = Ticket(
            id=1,
            name="Problema no sistema",
            status=TicketStatus.NOVO,
            priority=TicketPriority.ALTA,
            created_at=now,
            updated_at=now
        )
        
        assert ticket.id == 1
        assert ticket.name == "Problema no sistema"
        assert ticket.status == TicketStatus.NOVO
        assert ticket.priority == TicketPriority.ALTA
        assert ticket.created_at == now
        assert ticket.updated_at == now
        assert ticket.assigned_group_id is None
        assert ticket.assigned_user_id is None
        assert ticket.resolved_at is None
        assert ticket.closed_at is None

    def test_create_ticket_with_factory(self):
        """Testa criação de ticket usando factory."""
        ticket = TicketFactory()
        
        assert isinstance(ticket.id, int)
        assert isinstance(ticket.name, str)
        assert isinstance(ticket.status, TicketStatus)
        assert isinstance(ticket.priority, TicketPriority)
        assert ticket.created_at is not None
        assert ticket.updated_at is not None

    def test_resolved_ticket_factory(self):
        """Testa factory de ticket resolvido."""
        ticket = ResolvedTicketFactory()
        
        assert ticket.status == TicketStatus.SOLUCIONADO
        assert ticket.resolved_at is not None
        assert ticket.resolved_at > ticket.created_at

    def test_ticket_status_enum_values(self):
        """Testa valores do enum TicketStatus."""
        assert TicketStatus.NOVO.value == 1
        assert TicketStatus.PROCESSANDO_ATRIBUIDO.value == 2
        assert TicketStatus.PROCESSANDO_PLANEJADO.value == 3
        assert TicketStatus.PENDENTE.value == 4
        assert TicketStatus.SOLUCIONADO.value == 5
        assert TicketStatus.FECHADO.value == 6

    def test_ticket_priority_enum_values(self):
        """Testa valores do enum TicketPriority."""
        assert TicketPriority.MUITO_BAIXA.value == 1
        assert TicketPriority.BAIXA.value == 2
        assert TicketPriority.MEDIA.value == 3
        assert TicketPriority.ALTA.value == 4
        assert TicketPriority.MUITO_ALTA.value == 5
        assert TicketPriority.CRITICA.value == 6

    def test_is_resolved_method(self):
        """Testa método is_resolved."""
        resolved_ticket = TicketFactory(status=TicketStatus.SOLUCIONADO)
        closed_ticket = TicketFactory(status=TicketStatus.FECHADO)
        new_ticket = TicketFactory(status=TicketStatus.NOVO)
        
        assert resolved_ticket.is_resolved() is True
        assert closed_ticket.is_resolved() is True
        assert new_ticket.is_resolved() is False

    def test_is_pending_method(self):
        """Testa método is_pending."""
        pending_ticket = TicketFactory(status=TicketStatus.PENDENTE)
        new_ticket = TicketFactory(status=TicketStatus.NOVO)
        
        assert pending_ticket.is_pending() is True
        assert new_ticket.is_pending() is False

    def test_is_in_progress_method(self):
        """Testa método is_in_progress."""
        assigned_ticket = TicketFactory(status=TicketStatus.PROCESSANDO_ATRIBUIDO)
        planned_ticket = TicketFactory(status=TicketStatus.PROCESSANDO_PLANEJADO)
        new_ticket = TicketFactory(status=TicketStatus.NOVO)
        
        assert assigned_ticket.is_in_progress() is True
        assert planned_ticket.is_in_progress() is True
        assert new_ticket.is_in_progress() is False

    def test_ticket_equality(self):
        """Testa igualdade entre tickets."""
        now = datetime.now(timezone.utc)
        ticket1 = Ticket(
            id=1,
            name="Test",
            status=TicketStatus.NOVO,
            priority=TicketPriority.MEDIA,
            created_at=now,
            updated_at=now
        )
        ticket2 = Ticket(
            id=1,
            name="Test",
            status=TicketStatus.NOVO,
            priority=TicketPriority.MEDIA,
            created_at=now,
            updated_at=now
        )
        ticket3 = Ticket(
            id=2,
            name="Test",
            status=TicketStatus.NOVO,
            priority=TicketPriority.MEDIA,
            created_at=now,
            updated_at=now
        )
        
        assert ticket1 == ticket2
        assert ticket1 != ticket3

    def test_ticket_string_representation(self):
        """Testa representação em string do ticket."""
        ticket = TicketFactory(id=123, name="Test Ticket")
        ticket_str = str(ticket)
        
        assert "123" in ticket_str
        assert "Test Ticket" in ticket_str
