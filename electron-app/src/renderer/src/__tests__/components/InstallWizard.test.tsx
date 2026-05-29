import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import InstallWizard from '../../components/InstallWizard'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const minecraftGame = GAMES.find(g => g.id === 'minecraft')!
const palworldGame = GAMES.find(g => g.id === 'palworld')!

const instance: ServerInstance = {
  id: 'mc-wizard-1',
  gameId: 'minecraft',
  name: 'Install Test',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

const onClose = vi.fn()

describe('InstallWizard — initial state', () => {
  it('renders the game name in the heading', () => {
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    expect(screen.getByText(/Install Minecraft Server/i)).toBeInTheDocument()
  })

  it('shows the instance name in the subtitle', () => {
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    expect(screen.getByText(/Install Test/i)).toBeInTheDocument()
  })

  it('renders Minecraft custom step labels', () => {
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    expect(screen.getByText(/Check Java/i)).toBeInTheDocument()
    expect(screen.getByText(/Download server JAR/i)).toBeInTheDocument()
    expect(screen.getByText(/Configure/i)).toBeInTheDocument()
  })

  it('renders default Steam step labels for non-Minecraft games', () => {
    const steamInstance = { ...instance, gameId: 'palworld' }
    render(<InstallWizard game={palworldGame} instance={steamInstance} onClose={onClose} />)
    expect(screen.getByText(/Download SteamCMD/i)).toBeInTheDocument()
    expect(screen.getByText(/Install server files/i)).toBeInTheDocument()
    expect(screen.getByText(/Complete/i)).toBeInTheDocument()
  })

  it('shows Start Installation and Cancel buttons before starting', () => {
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    expect(screen.getByRole('button', { name: /Start Installation/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument()
  })

  it('does not show the log output pane before starting', () => {
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    expect(screen.queryByText(/Waiting for output/i)).not.toBeInTheDocument()
  })

  it('calls onClose when the pre-start Cancel is clicked', async () => {
    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Cancel/i }))
    expect(onClose).toHaveBeenCalledOnce()
  })
})

describe('InstallWizard — after starting', () => {
  it('calls startInstall with correct parameters when Start Installation is clicked', async () => {
    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))
    expect(mockApi.startInstall).toHaveBeenCalledWith(
      'minecraft',
      'mc-wizard-1',
      minecraftGame.steamAppId,
      minecraftGame.installMode,
      minecraftGame.installOnce
    )
  })

  it('shows the log pane after starting', async () => {
    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))
    await waitFor(() => {
      expect(screen.getByText(/Waiting for output/i)).toBeInTheDocument()
    })
  })

  it('hides the pre-start Cancel button after starting', async () => {
    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /Start Installation/i })).not.toBeInTheDocument()
    })
  })
})

describe('InstallWizard — event-driven state transitions', () => {
  it('shows error banner when install:error fires', async () => {
    // Capture the `on` handler so we can trigger it manually
    let errorHandler: ((msg: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'install:error') errorHandler = fn as (msg: unknown) => void
      return vi.fn()
    })

    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))

    // Simulate error event
    errorHandler?.('SteamCMD failed with exit code 1')

    await waitFor(() => {
      expect(screen.getByText(/SteamCMD failed/i)).toBeInTheDocument()
    })
  })

  it('shows Done button when install:done fires with true', async () => {
    let doneHandler: ((ok: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'install:done') doneHandler = fn as (ok: unknown) => void
      return vi.fn()
    })

    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))

    doneHandler?.(true)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Done/i })).toBeInTheDocument()
    })
  })

  it('calls onClose when Done is clicked after successful install', async () => {
    let doneHandler: ((ok: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'install:done') doneHandler = fn as (ok: unknown) => void
      return vi.fn()
    })

    const user = userEvent.setup()
    render(<InstallWizard game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Start Installation/i }))
    doneHandler?.(true)
    await waitFor(() => screen.getByRole('button', { name: /Done/i }))
    await user.click(screen.getByRole('button', { name: /Done/i }))
    expect(onClose).toHaveBeenCalled()
  })
})
