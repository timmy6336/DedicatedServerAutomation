import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ServerPanel from '../../components/ServerPanel'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const minecraftGame = GAMES.find(g => g.id === 'minecraft')!
const dstGame = GAMES.find(g => g.id === 'dst')!
const palworldGame = GAMES.find(g => g.id === 'palworld')!

const baseInstance: ServerInstance = {
  id: 'mc-test-1',
  gameId: 'minecraft',
  name: 'Survival World',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

const onInstanceUpdated = vi.fn()

function renderPanel(game = minecraftGame, instance = baseInstance) {
  return render(
    <ServerPanel game={game} instance={instance} onInstanceUpdated={onInstanceUpdated} />
  )
}

describe('ServerPanel — Hero', () => {
  it('shows the instance name as the heading', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Survival World/i })).toBeInTheDocument()
    })
  })

  it('shows the game name below the heading', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Minecraft')).toBeInTheDocument()
    })
  })

  it('shows the game genre badge', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/Sandbox \/ Survival/i)).toBeInTheDocument()
    })
  })

  it('shows "Checking" status initially', async () => {
    renderPanel()
    expect(screen.getByText('Checking')).toBeInTheDocument()
  })

  it('shows "Not Installed" once isInstalled resolves false', async () => {
    mockApi.isInstalled.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Not Installed')).toBeInTheDocument()
    })
  })

  it('shows "Offline" when installed but not running', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument()
    })
  })

  it('shows "Online" when running', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(true)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Online')).toBeInTheDocument()
    })
  })
})

describe('ServerPanel — Tab bar', () => {
  it('always shows Overview, Logs, and Backups tabs', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Overview/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Logs/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Backups/i })).toBeInTheDocument()
    })
  })

  it('shows Mods tab for Minecraft', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Mods/i })).toBeInTheDocument()
    })
  })

  it('does NOT show Mods tab for DST', async () => {
    const dstInstance = { ...baseInstance, gameId: 'dst' }
    renderPanel(dstGame, dstInstance)
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /Mods/i })).not.toBeInTheDocument()
    })
  })

  it('switching to Logs tab shows the LogsPanel', async () => {
    const user = userEvent.setup()
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Logs/i }))
    await user.click(screen.getByRole('button', { name: /Logs/i }))
    await waitFor(() => {
      expect(screen.getByText(/Server Log/i)).toBeInTheDocument()
    })
  })

  it('switching to Backups tab shows the BackupsPanel', async () => {
    const user = userEvent.setup()
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Backups/i }))
    await user.click(screen.getByRole('button', { name: /Backups/i }))
    // Unique content from BackupsPanel empty state
    await waitFor(() => {
      expect(screen.getByText(/No backups yet/i)).toBeInTheDocument()
    })
  })

  it('shows mod count badge when enabledMods is non-empty', async () => {
    const instanceWithMods = { ...baseInstance, enabledMods: ['mod-a.jar', 'mod-b.jar'] }
    renderPanel(minecraftGame, instanceWithMods)
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })
})

describe('ServerPanel — Actions', () => {
  it('shows "Install Server" when not installed', async () => {
    mockApi.isInstalled.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Install Server/i })).toBeInTheDocument()
    })
  })

  it('shows "Start Server" and "Configure" when installed and stopped', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Start Server/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Configure/i })).toBeInTheDocument()
    })
  })

  it('shows "Stop Server" when running', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(true)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Stop Server/i })).toBeInTheDocument()
    })
  })

  it('shows "Uninstall" button when stopped', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Uninstall/i })).toBeInTheDocument()
    })
  })

  it('shows inline confirm dialog when Uninstall is clicked', async () => {
    const user = userEvent.setup()
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Uninstall/i }))
    await user.click(screen.getByRole('button', { name: /Uninstall/i }))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Yes, uninstall/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument()
    })
  })

  it('cancels uninstall when Cancel is clicked', async () => {
    const user = userEvent.setup()
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Uninstall/i }))
    await user.click(screen.getByRole('button', { name: /Uninstall/i }))
    await user.click(screen.getByRole('button', { name: /Cancel/i }))
    await waitFor(() => {
      // Confirm dialog hidden; Uninstall button should be back
      expect(screen.getByRole('button', { name: /Uninstall/i })).toBeInTheDocument()
    })
  })

  it('calls startServer when Start Server is clicked', async () => {
    const user = userEvent.setup()
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Start Server/i }))
    await user.click(screen.getByRole('button', { name: /Start Server/i }))
    expect(mockApi.startServer).toHaveBeenCalledWith(
      baseInstance.id,
      minecraftGame.id,
      minecraftGame.launchMode,
      expect.any(String),
      expect.any(Array),
      minecraftGame.installOnce
    )
  })

  it('opens ConfigModal when Configure is clicked', async () => {
    const user = userEvent.setup()
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(false)
    renderPanel()
    await waitFor(() => screen.getByRole('button', { name: /Configure/i }))
    await user.click(screen.getByRole('button', { name: /Configure/i }))
    await waitFor(() => {
      expect(screen.getByText(/Minecraft Configuration/i)).toBeInTheDocument()
    })
  })
})

describe('ServerPanel — Overview content', () => {
  it('shows About section with game description', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/iconic sandbox survival/i)).toBeInTheDocument()
    })
  })

  it('shows Required Ports section', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('25565')).toBeInTheDocument()
    })
  })

  it('shows Platforms section', async () => {
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText('Windows')).toBeInTheDocument()
      expect(screen.getByText('Linux')).toBeInTheDocument()
      expect(screen.getByText('macOS')).toBeInTheDocument()
    })
  })

  it('shows connection info when server is running', async () => {
    mockApi.isInstalled.mockResolvedValue(true)
    mockApi.isRunning.mockResolvedValue(true)
    mockApi.getLocalIp.mockResolvedValue('10.0.0.5')
    renderPanel()
    await waitFor(() => {
      expect(screen.getByText(/10\.0\.0\.5/)).toBeInTheDocument()
    })
  })
})
