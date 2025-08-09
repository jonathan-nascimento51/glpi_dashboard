import type { Meta, StoryObj } from '@storybook/react';
import { KpiCard } from './KpiCard';
const meta: Meta<typeof KpiCard> = { title: 'Dashboard/KpiCard', component: KpiCard };
export default meta;
type Story = StoryObj<typeof KpiCard>;
export const Ok: Story = { args: { title: 'N1', total: 20, open: 5, inProgress: 10, closed: 5 } };
export const Loading: Story = { args: { title: 'N1', total: 0, open: 0, inProgress: 0, closed: 0, loading: true } };
export const Error: Story = { args: { title: 'N1', total: 0, open: 0, inProgress: 0, closed: 0, error: 'Falha ao carregar' } };