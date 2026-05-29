import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Sidebar from '../../components/Sidebar'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const onSelectInstance = vi.fn()

const mockInstance: ServerInstance = {
  id: 'palworld-abc',
  gameId: 'palworld',
  name: 'Island Base',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

function renderSidebar(selectedInstance: ServerInstance | null = null) {
  return render(
    <Sidebar
      games={GAMES}
      selectedInstance={selectedInstance}
      onSelectInstance={onSelectInstance}
    />
  )
}

describe('Sidebar', () => {
  it('renders all 10 game rows', async () => {
    renderSidebar()
    await waitFor(() => {
      // Each game name should appear in the nav
      expect(screen.getByText('Palworld')).toBeInTheDocument()
      expect(screen.getByText('Valheim')).toBeInTheDocument()
      expect(screen.getByText('Minecraft')).toBeInTheDocument()
      expect(screen.getByText('Rust')).toBeInTheDocument()
      expect(screen.getByText('V Rising')).toBeInTheDocument()
      expect(screen.getByText('Enshrouded')).toBeInTheDocument()
    })
  })

  it('calls listInstances for every game on mount', async () => {
    renderSidebar()
    await waitFor(() => {
      expect(mockApi.listInstances).toHaveBeenCalledTimes(GAMES.length)
    })
  })

  it('auto-selects the first instance available when none is selected', async () => {
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderSidebar(null)
    await waitFor(() => {
      expect(onSelectInstance).toHaveBeenCalledWith(mockInstance, expect.objectContaining({ id: 'palworld' }))
    })
  })

  it('shows the instance count badge when instances exist', async () => {
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderSidebar()
    await waitFor(() => {
      // The count "1" should appear for Palworld
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('expands a collapsed game section when the game row is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'valheim') return [{ ...mockInstance, id: 'valheim-1', gameId: 'valheim', name: 'Nordic Realm' }]
      return []
    })
    renderSidebar()
    await waitFor(() => screen.getByText('Valheim'))

    // Valheim should not initially show instances (Palworld is expanded by default)
    expect(screen.queryByText('Nordic Realm')).not.toBeInTheDocument()

    await user.click(screen.getByText('Valheim'))
    await waitFor(() => {
      expect(screen.getByText('Nordic Realm')).toBeInTheDocument()
    })
  })

  it('shows "New server" button inside expanded game section', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockResolvedValue([])
    renderSidebar()
    await waitFor(() => screen.getByText('Palworld'))

    // Palworld is expanded by default (first game)
    await waitFor(() => {
      expect(screen.getByText('New server')).toBeInTheDocument()
    })
  })

  it('opens NewServerModal when "New server" is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockResolvedValue([])
    renderSidebar()
    await waitFor(() => screen.getByText('New server'))
    await user.click(screen.getByText('New server'))
    // Modal opens — should show "New Palworld Server"
    await waitFor(() => {
      expect(screen.getByText(/New Palworld Server/i)).toBeInTheDocument()
    })
  })

  it('calls onSelectInstance when an instance button is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listInstances.mockImplementation(async (gameId: string) => {
      if (gameId === 'palworld') return [mockInstance]
      return []
    })
    renderSidebar()
    await waitFor(() => screen.getByText('Island Base'))
    await user.click(screen.getByText('Island Base'))
    expect(onSelectInstance).toHaveBeenCalledWith(mockInstance, expect.objectContaining({ id: 'palworld' }))
  })

  it('renders the version footer', () => {
    renderSidebar()
    expect(screen.getByText('v2.0.0')).toBeInTheDocument()
  })
})
