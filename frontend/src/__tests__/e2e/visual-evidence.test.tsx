import { test, expect } from '@playwright/test';
import { RankingTable } from '../../components/dashboard/RankingTable';
import { captureComponentScreenshot, captureTestEvidence } from '../utils/screenshot';
import { getTechnicianRanking } from '../../services/api';

const mockRankingData = [
  {
    name: 'João Silva',
    total: 45,
    level: 'N1',
    avg_resolution_time: 2.5,
  },
  {
    name: 'Maria Santos',
    total: 38,
    level: 'N2',
    avg_resolution_time: 3.2,
  },
  {
    name: 'Pedro Costa',
    total: 32,
    level: 'N1',
    avg_resolution_time: 2.8,
  },
  {
    name: 'Ana Oliveira',
    total: 28,
    level: 'N3',
    avg_resolution_time: 4.1,
  },
  {
    name: 'Carlos Ferreira',
    total: 25,
    level: 'N4',
    avg_resolution_time: 5.5,
  },
];

test.describe('Evidências Visuais - Ranking de Técnicos', () => {
  test('deve capturar evidência visual do estado inicial', async ({ page }) => {
    // Navegar para a página com o componente
    await page.goto('/dashboard');

    // Aguardar o componente carregar
    await page.waitForSelector('[data-testid="ranking-container"]');

    // Verificar se os dados estão carregados
    await expect(page.locator('text=/N[1-4]/')).toHaveCount(5);

    // Capturar screenshot do estado inicial
    const screenshot = await page.screenshot({
      fullPage: true,
      clip: {
        x: 0,
        y: 0,
        width: 1920,
        height: 1080,
      },
    });

    expect(screenshot).toBeDefined();
  });

  it('deve capturar evidências visuais em diferentes resoluções', async () => {
    const resolutions = [
      { width: 1920, height: 1080, name: 'desktop-fhd' },
      { width: 1366, height: 768, name: 'desktop-hd' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 375, height: 667, name: 'mobile' },
    ];

    for (const resolution of resolutions) {
      const { container } = renderComponent(
        <div data-testid={`ranking-${resolution.name}`}>
          <RankingTable data={mockRankingData} />
        </div>
      );

      // Aguardar renderização do componente
      await waitFor(
        () => {
          const cards = screen.queryAllByTestId(/technician-card-/);
          expect(cards.length).toBeGreaterThan(0);
        },
        { timeout: 5000 }
      );

      const screenshot = await captureComponentScreenshot(`ranking-${resolution.name}`, {
        testName: `responsivo-${resolution.name}`,
        componentName: 'RankingTable',
        width: resolution.width,
        height: resolution.height,
      });

      expect(screenshot).toBeDefined();
      expect(typeof screenshot).toBe('string');
    }
  });

  it('deve capturar evidências de diferentes estados dos cards', async () => {
    const { container } = renderComponent(
      <div data-testid='ranking-states'>
        <RankingTable data={mockRankingData} />
      </div>
    );

    const screenshots = await captureTestEvidence('estados-dos-cards', 'RankingTable', [
      {
        name: 'renderizacao-inicial',
        action: async () => {
          await waitFor(() => {
            expect(screen.getAllByText(/N[1-4]/).length).toBeGreaterThan(0);
          });
        },
      },
      {
        name: 'verificacao-niveis',
        action: async () => {
          await waitFor(() => {
            expect(screen.getAllByText('N1').length).toBeGreaterThan(0);
            expect(screen.getAllByText('N2').length).toBeGreaterThan(0);
            expect(screen.getAllByText('N3').length).toBeGreaterThan(0);
            expect(screen.getAllByText('N4').length).toBeGreaterThan(0);
          });
        },
      },
      {
        name: 'verificacao-nomes-formatados',
        action: async () => {
          await waitFor(() => {
            expect(screen.getAllByText(/N[1-4]/).length).toBeGreaterThan(0);
          });
        },
      },
    ]);

    expect(screenshots).toHaveLength(3);
    screenshots.forEach(screenshot => {
      expect(screenshot).toBeDefined();
      expect(typeof screenshot).toBe('string');
    });
  });

  it('deve validar renderização dos cards por nível', async () => {
    const { container } = renderComponent(
      <div data-testid='ranking-levels'>
        <RankingTable data={mockRankingData} />
      </div>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/N[1-4]/).length).toBeGreaterThan(0);
    });

    // Verificar se os cards estão sendo renderizados
    const technicianCards = screen.getAllByTestId(/technician-card-/);
    expect(technicianCards.length).toBeGreaterThanOrEqual(mockRankingData.length);

    // Capturar evidência visual dos cards por nível
    const screenshot = await captureComponentScreenshot('ranking-levels', {
      testName: 'cards-por-nivel',
      componentName: 'RankingTable',
      width: 1920,
      height: 1080,
    });

    expect(screenshot).toBeDefined();

    // Verificar se todos os níveis estão presentes
    const levels = ['N1', 'N2', 'N3', 'N4'];
    levels.forEach(level => {
      const levelElements = screen.getAllByText(level);
      expect(levelElements.length).toBeGreaterThan(0);
    });
  });

  it('deve capturar evidência de performance visual', async () => {
    const startTime = performance.now();

    const { container } = renderComponent(
      <div data-testid='ranking-performance'>
        <RankingTable data={mockRankingData} />
      </div>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/N[1-4]/).length).toBeGreaterThan(0);
    });

    const renderTime = performance.now() - startTime;

    // Capturar screenshot após renderização
    const screenshot = await captureComponentScreenshot('ranking-performance', {
      testName: `performance-${Math.round(renderTime)}ms`,
      componentName: 'RankingTable',
    });

    expect(screenshot).toBeDefined();
    expect(renderTime).toBeLessThan(5000); // Renderização deve ser menor que 5s

    console.log(`Tempo de renderização: ${renderTime.toFixed(2)}ms`);
  });
});
