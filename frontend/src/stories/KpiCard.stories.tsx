import type { Meta, StoryObj } from '@storybook/react';
import { DashboardCard } from '../domains/dashboard';
const meta: Meta<typeof DashboardCard> = { title: 'Dashboard/DashboardCard', component: DashboardCard };
export default meta;
type Story = StoryObj<typeof DashboardCard>;
export const Ok: Story = { args: { title: 'N1', total: 20, open: 5, inProgress: 10, closed: 5 } };
export const Loading: Story = { args: { title: 'N1', total: 0, open: 0, inProgress: 0, closed: 0, loading: true } };
export const Error: Story = { args: { title: 'N1', total: 0, open: 0, inProgress: 0, closed: 0, error: 'Falha ao carregar' } };
