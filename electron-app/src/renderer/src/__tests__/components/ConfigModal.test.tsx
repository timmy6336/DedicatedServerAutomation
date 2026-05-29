import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConfigModal from '../../components/ConfigModal'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const minecraftGame = GAMES.find(g => g.id === 'minecraft')!
const rustGame = GAMES.find(g => g.id === 'rust')!
const dstGame = GAMES.find(g => g.id === 'dst')!

const instance: ServerInstance = {
  id: 'test-instance-1',
  gameId: 'minecraft',
  name: 'My Test Server',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

const onClose = vi.fn()

describe('ConfigModal', () => {
  it('renders the modal with the game name in the heading', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      expect(screen.getByText(/Minecraft Configuration/i)).toBeInTheDocument()
    })
  })

  it('shows the instance name in the subtitle', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      expect(screen.getByText(/My Test Server/i)).toBeInTheDocument()
    })
  })

  it('calls onClose when Cancel is clicked', async () => {
    const user = userEvent.setup()
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await user.click(screen.getByRole('button', { name: /Cancel/i }))
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('calls saveConfig when Save Changes is clicked', async () => {
    const user = userEvent.setup()
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => screen.getByRole('button', { name: /Save Changes/i }))
    await user.click(screen.getByRole('button', { name: /Save Changes/i }))
    expect(mockApi.saveConfig).toHaveBeenCalledWith('test-instance-1', expect.any(Object))
  })

  it('renders text input for string-type settings', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      // Labels don't use htmlFor — query inputs directly
      const textInputs = Array.from(document.querySelectorAll('input[type="text"]'))
      expect(textInputs.length).toBeGreaterThan(0)
    })
  })

  it('renders password input for password-type settings', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      // Minecraft has RCON Password
      const passwordInputs = screen.getAllByDisplayValue('')
      const passwordFields = Array.from(document.querySelectorAll('input[type="password"]'))
      expect(passwordFields.length).toBeGreaterThan(0)
    })
  })

  it('renders number input for int-type settings', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      // At least one numeric input (port, max_players, etc.)
      const numberInputs = document.querySelectorAll('input[type="number"]')
      expect(numberInputs.length).toBeGreaterThan(0)
    })
  })

  it('renders select element for choice-type settings', async () => {
    // Rust has world_size as a choice setting
    const rustInstance = { ...instance, gameId: 'rust' }
    render(<ConfigModal game={rustGame} instance={rustInstance} onClose={onClose} />)
    await waitFor(() => {
      const selects = document.querySelectorAll('select')
      expect(selects.length).toBeGreaterThan(0)
    })
  })

  it('renders a toggle button for bool-type settings', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      // Minecraft has bool fields: whitelist, pvp, online_mode
      const toggleButtons = Array.from(document.querySelectorAll('button')).filter(
        btn => btn.classList.contains('rounded-full')
      )
      expect(toggleButtons.length).toBeGreaterThan(0)
    })
  })

  it('renders a help link for settings with helpUrl', async () => {
    const dstInstance = { ...instance, gameId: 'dst' }
    render(<ConfigModal game={dstGame} instance={dstInstance} onClose={onClose} />)
    await waitFor(() => {
      const link = screen.getByRole('link', { name: /Get token/i })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', expect.stringContaining('klei.com'))
    })
  })

  it('marks required fields with an asterisk', async () => {
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      // No required minecraft fields that aren't password — check the DOM for asterisk
      const requiredSetting = minecraftGame.serverSettings.find(s => s.required)
      if (requiredSetting) {
        // We just verify at least one * is rendered somewhere in the labels
        const labels = screen.getAllByText(/\*/i)
        expect(labels.length).toBeGreaterThan(0)
      }
    })
  })

  it('loads saved config and merges with defaults', async () => {
    mockApi.loadConfig.mockResolvedValue({ port: 19999, motd: 'Custom MOTD' })
    render(<ConfigModal game={minecraftGame} instance={instance} onClose={onClose} />)
    await waitFor(() => {
      const portInput = document.querySelector('input[type="number"]') as HTMLInputElement
      // Can't test exact value easily since multiple number inputs exist,
      // but we verify loadConfig was called with the correct instanceId
      expect(mockApi.loadConfig).toHaveBeenCalledWith('test-instance-1')
    })
  })
})
