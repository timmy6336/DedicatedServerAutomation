import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InstanceList from '../../components/InstanceList'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const onSelectInstance = vi.fn()
const onInstanceCreated = vi.fn()

const palworld = GAMES.find(g => g.id === 'palworld')!

const mockInstance: ServerInstance = {
  id: 'palworld-abc',
  gameId: 'palworld',
  name: 'Island Base',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

function renderInstanceList(
  game = palworld,
  selectedInstance: ServerInstance | null = null
) {
  return render(
    <InstanceList
      game={game}
      selectedInstance={selectedInstance}
      onSelectInstance={onSelectInstance}
      onInstanceCreated={onInstanceCreated}
    />
  )
}

describe('InstanceList', () => {
  it('calls listInstances on mount for the current game', async () => {
    renderInstanceList()
    await waitFor(() => {
      expect(mockApi.listInstances).toHaveBeenCalledWith('palworld')
    })
  })

  it('renders instance cards after loading', async () => {
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderInstanceList()
    await waitFor(() => {
      expect(screen.getByText('Island Base')).toBeInTheDocument()
    })
  })

  it('calls onSelectInstance when an instance card is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderInstanceList()
    await waitFor(() => screen.getByText('Island Base'))
    await user.click(screen.getByText('Island Base'))
    expect(onSelectInstance).toHaveBeenCalledWith(mockInstance, expect.objectContaining({ id: 'palworld' }))
  })

  it('shows the instance count badge when instances exist', async () => {
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderInstanceList()
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('shows "New server" button when instances exist', async () => {
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderInstanceList()
    await waitFor(() => {
      expect(screen.getByText('New server')).toBeInTheDocument()
    })
  })

  it('opens NewServerModal when "New server" is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderInstanceList()
    await waitFor(() => screen.getByText('New server'))
    await user.click(screen.getByText('New server'))
    await waitFor(() => {
      expect(screen.getByText(/New Palworld Server/i)).toBeInTheDocument()
    })
  })

  it('shows empty state with "Create one!" button when no instances', async () => {
    mockApi.listInstances.mockResolvedValue([])
    renderInstanceList()
    await waitFor(() => {
      expect(screen.getByText(/No servers for Palworld/i)).toBeInTheDocument()
      expect(screen.getByText('Create one!')).toBeInTheDocument()
    })
  })

  it('opens NewServerModal when "Create one!" is clicked on empty state', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockResolvedValue([])
    renderInstanceList()
    await waitFor(() => screen.getByText('Create one!'))
    await user.click(screen.getByText('Create one!'))
    await waitFor(() => {
      expect(screen.getByText(/New Palworld Server/i)).toBeInTheDocument()
    })
  })
})
