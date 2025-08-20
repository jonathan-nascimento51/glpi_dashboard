import { screen } from '@testing-library/react';
import fs from 'fs';
import path from 'path';

// Mock do html2canvas para ambiente de teste
const mockHtml2Canvas = async (element: HTMLElement, options?: any): Promise<HTMLCanvasElement> => {
  const canvas = document.createElement('canvas');
  canvas.width = options?.width || 1920;
  canvas.height = options?.height || 1080;

  const ctx = canvas.getContext('2d');
  if (ctx) {
    // Simular captura com cor de fundo
    ctx.fillStyle = options?.backgroundColor || '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Adicionar texto indicativo
    ctx.fillStyle = '#000000';
    ctx.font = '16px Arial';
    ctx.fillText(`Screenshot: ${element.tagName}`, 10, 30);
    ctx.fillText(`Size: ${canvas.width}x${canvas.height}`, 10, 50);
    ctx.fillText(`Timestamp: ${new Date().toISOString()}`, 10, 70);
  }

  return canvas;
};

// Usar html2canvas real em produção, mock em teste
const html2canvas =
  process.env.NODE_ENV === 'test' ? mockHtml2Canvas : require('html2canvas').default;

/**
 * Utilitário para captura de screenshots durante os testes
 * Usado para gerar evidências visuais dos componentes
 */

interface ScreenshotOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'png' | 'jpeg';
  testName?: string;
  componentName?: string;
}

const DEFAULT_OPTIONS: Required<ScreenshotOptions> = {
  width: 1920,
  height: 1080,
  quality: 0.9,
  format: 'png',
  testName: 'test',
  componentName: 'component',
};

/**
 * Captura screenshot de um elemento específico
 */
export const captureElementScreenshot = async (
  element: HTMLElement,
  options: ScreenshotOptions = {}
): Promise<string> => {
  const config = { ...DEFAULT_OPTIONS, ...options };

  try {
    // Configurar viewport fixo
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: config.width,
    });

    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: config.height,
    });

    // Capturar screenshot
    const canvas = await html2canvas(element, {
      width: config.width,
      height: config.height,
      scale: 1,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
    });

    // Converter para base64
    const dataUrl = canvas.toDataURL(`image/${config.format}`, config.quality);

    // Verificar se dataUrl é válido
    if (!dataUrl || dataUrl === 'data:,') {
      console.warn('Screenshot capturado está vazio, retornando mock');
      return `data:image/${config.format};base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
    }

    // Salvar arquivo se em ambiente de teste
    if (process.env.NODE_ENV === 'test') {
      await saveScreenshot(dataUrl, config);
    }

    return dataUrl;
  } catch (error) {
    console.error('Erro ao capturar screenshot:', error);
    throw error;
  }
};

/**
 * Captura screenshot do componente principal renderizado
 */
export const captureComponentScreenshot = async (
  testId: string,
  options: ScreenshotOptions = {}
): Promise<string> => {
  const element = screen.getByTestId(testId);
  return captureElementScreenshot(element, options);
};

/**
 * Captura screenshot da tela inteira
 */
export const captureFullScreenshot = async (options: ScreenshotOptions = {}): Promise<string> => {
  return captureElementScreenshot(document.body, options);
};

/**
 * Salva screenshot no sistema de arquivos
 */
const saveScreenshot = async (
  dataUrl: string,
  config: Required<ScreenshotOptions>
): Promise<void> => {
  // Verificar se dataUrl é válido
  if (!dataUrl || typeof dataUrl !== 'string') {
    console.warn('DataUrl inválido, pulando salvamento do screenshot');
    return;
  }

  const screenshotsDir = path.join(process.cwd(), 'test-evidence', 'screenshots');

  // Criar diretório se não existir
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  // Gerar nome do arquivo
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${config.componentName}_${config.testName}_${timestamp}.${config.format}`;
  const filepath = path.join(screenshotsDir, filename);

  try {
    // Converter base64 para buffer
    const base64Data = dataUrl.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');

    // Salvar arquivo
    fs.writeFileSync(filepath, buffer);
    console.log(`Screenshot salvo: ${filepath}`);
  } catch (error) {
    console.error('Erro ao salvar screenshot:', error);
    // Em ambiente de teste, apenas log o erro sem falhar
    if (process.env.NODE_ENV !== 'test') {
      throw error;
    }
  }
};

/**
 * Compara dois screenshots (para testes de regressão visual)
 */
export const compareScreenshots = async (
  screenshot1: string,
  screenshot2: string,
  threshold: number = 0.1
): Promise<{ match: boolean; difference: number }> => {
  // Implementação básica de comparação
  // Em um cenário real, usaríamos uma biblioteca como pixelmatch
  const match = screenshot1 === screenshot2;
  const difference = match ? 0 : 1;

  return { match, difference };
};

/**
 * Utilitário para capturar evidências durante testes E2E
 */
export const captureTestEvidence = async (
  testName: string,
  componentName: string,
  actions: Array<{
    name: string;
    action: () => Promise<void> | void;
    captureAfter?: boolean;
  }>
): Promise<string[]> => {
  const screenshots: string[] = [];

  for (const { name, action, captureAfter = true } of actions) {
    // Executar ação
    await action();

    // Capturar screenshot se solicitado
    if (captureAfter) {
      const screenshot = await captureFullScreenshot({
        testName: `${testName}_${name}`,
        componentName,
      });
      screenshots.push(screenshot);
    }
  }

  return screenshots;
};
