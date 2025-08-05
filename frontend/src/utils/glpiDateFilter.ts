/**
 * Utilitários para implementar filtros de data com a API do GLPI
 * Baseado na documentação oficial do GLPI REST API
 */

// Interface para os critérios de busca do GLPI
interface GLPISearchCriteria {
  field: string;
  searchtype: 'morethan' | 'lessthan' | 'equals' | 'contains';
  value: string;
  link?: 'AND' | 'OR';
}

// Interface para parâmetros de busca
interface GLPISearchParams {
  is_deleted: string;
  glpilist_limit: string;
  criteria: GLPISearchCriteria[];
}

/**
 * Converte uma data JavaScript para o formato esperado pelo GLPI
 * @param date Data a ser convertida
 * @returns String no formato YYYY-MM-DD HH:mm:ss
 */
export function toGLPIDate(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

/**
 * Constrói os critérios de filtro por data para a API do GLPI
 * @param startDate Data inicial
 * @param endDate Data final
 * @param dateFieldId ID do campo de data no GLPI (ex: 15 para date_creation)
 * @returns Array de critérios de busca
 */
export function buildDateCriteria(
  startDate: string,
  endDate: string,
  dateFieldId: number = 15 // 15 é comumente usado para date_creation
): GLPISearchCriteria[] {
  const start = new Date(startDate);
  start.setHours(0, 0, 0, 0);
  
  const end = new Date(endDate);
  end.setHours(23, 59, 59, 999);

  return [
    {
      field: dateFieldId.toString(),
      searchtype: 'morethan',
      value: toGLPIDate(start),
      link: 'AND'
    },
    {
      field: dateFieldId.toString(),
      searchtype: 'lessthan',
      value: toGLPIDate(end),
      link: 'AND'
    }
  ];
}

/**
 * Constrói a URL completa para busca de tickets com filtro de data
 * @param startDate Data inicial
 * @param endDate Data final
 * @param groupIds IDs dos grupos (opcional)
 * @param dateFieldId ID do campo de data
 * @param groupFieldId ID do campo de grupo
 * @returns URL para a API do GLPI
 */
export function buildTicketSearchURL(
  startDate: string,
  endDate: string,
  groupIds: number[] = [],
  dateFieldId: number = 15,
  groupFieldId: number = 71
): string {
  const params = new URLSearchParams({
    'is_deleted': '0',
    'glpilist_limit': '10000'
  });

  // Adicionar critérios de data
  const dateCriteria = buildDateCriteria(startDate, endDate, dateFieldId);
  dateCriteria.forEach((criteria, index) => {
    params.set(`criteria[${index}][field]`, criteria.field);
    params.set(`criteria[${index}][searchtype]`, criteria.searchtype);
    params.set(`criteria[${index}][value]`, criteria.value);
    if (criteria.link) {
      params.set(`criteria[${index}][link]`, criteria.link);
    }
  });

  // Adicionar critérios de grupo se fornecidos
  groupIds.forEach((groupId, index) => {
    const criteriaIndex = dateCriteria.length + index;
    params.set(`criteria[${criteriaIndex}][field]`, groupFieldId.toString());
    params.set(`criteria[${criteriaIndex}][searchtype]`, 'equals');
    params.set(`criteria[${criteriaIndex}][value]`, groupId.toString());
    params.set(`criteria[${criteriaIndex}][link]`, 'AND');
  });

  return `/apirest.php/search/Ticket?${params.toString()}`;
}

/**
 * Processa a resposta da API do GLPI e agrupa os tickets por status
 * @param tickets Array de tickets retornados pela API
 * @returns Objeto com contadores por status
 */
export function processTicketsByStatus(tickets: any[]): Record<string, number> {
  const statusCounts: Record<string, number> = {
    'new': 0,
    'assigned': 0,
    'planned': 0,
    'waiting': 0,
    'solved': 0,
    'closed': 0
  };

  tickets.forEach(ticket => {
    const status = ticket.status;
    switch (status) {
      case 1: // New
        statusCounts.new++;
        break;
      case 2: // Processing (assigned)
        statusCounts.assigned++;
        break;
      case 3: // Planned
        statusCounts.planned++;
        break;
      case 4: // Pending
        statusCounts.waiting++;
        break;
      case 5: // Solved
        statusCounts.solved++;
        break;
      case 6: // Closed
        statusCounts.closed++;
        break;
    }
  });

  return statusCounts;
}

/**
 * Processa tickets por nível de atendimento
 * @param tickets Array de tickets
 * @returns Objeto com contadores por nível
 */
export function processTicketsByLevel(tickets: any[]): Record<string, Record<string, number>> {
  const levelCounts: Record<string, Record<string, number>> = {
    'n1': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 },
    'n2': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 },
    'n3': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 },
    'n4': { novos: 0, progresso: 0, pendentes: 0, resolvidos: 0 }
  };

  tickets.forEach(ticket => {
    // Determinar nível baseado no grupo ou categoria
    const level = determineTicketLevel(ticket);
    const status = mapTicketStatus(ticket.status);
    
    if (levelCounts[level] && levelCounts[level][status] !== undefined) {
      levelCounts[level][status]++;
    }
  });

  return levelCounts;
}

/**
 * Determina o nível do ticket baseado em regras de negócio
 * @param ticket Objeto do ticket
 * @returns Nível do ticket (n1, n2, n3, n4)
 */
function determineTicketLevel(ticket: any): string {
  // Implementar lógica específica baseada nos grupos ou categorias
  // Esta é uma implementação exemplo - ajustar conforme necessário
  const groupId = ticket.groups_id_assign || ticket.groups_id;
  
  if (groupId >= 1 && groupId <= 10) return 'n1';
  if (groupId >= 11 && groupId <= 20) return 'n2';
  if (groupId >= 21 && groupId <= 30) return 'n3';
  return 'n4';
}

/**
 * Mapeia o status numérico do GLPI para string
 * @param status Status numérico
 * @returns Status em string
 */
function mapTicketStatus(status: number): string {
  switch (status) {
    case 1: return 'novos';
    case 2: return 'progresso';
    case 4: return 'pendentes';
    case 5:
    case 6: return 'resolvidos';
    default: return 'novos';
  }
}

/**
 * Exemplo de uso completo
 */
export const GLPIDateFilterExample = {
  /**
   * Busca métricas filtradas por data
   */
  async getFilteredMetrics(
    startDate: string,
    endDate: string,
    sessionToken: string,
    appToken: string,
    baseURL: string = 'http://localhost/glpi'
  ) {
    try {
      // Construir URL de busca
      const searchURL = buildTicketSearchURL(startDate, endDate);
      const fullURL = `${baseURL}${searchURL}`;

      // Fazer requisição
      const response = await fetch(fullURL, {
        headers: {
          'Session-Token': sessionToken,
          'App-Token': appToken,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Processar dados
      const tickets = data.data || [];
      const statusCounts = processTicketsByStatus(tickets);
      const levelCounts = processTicketsByLevel(tickets);

      return {
        total: tickets.length,
        novos: statusCounts.new,
        progresso: statusCounts.assigned + statusCounts.planned,
        pendentes: statusCounts.waiting,
        resolvidos: statusCounts.solved + statusCounts.closed,
        niveis: levelCounts,
        rawData: tickets
      };
    } catch (error) {
      console.error('Erro ao buscar métricas filtradas:', error);
      throw error;
    }
  }
};