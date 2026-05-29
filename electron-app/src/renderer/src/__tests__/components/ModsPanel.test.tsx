import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ModsPanel from '../../components/ModsPanel'
import { GAMES } from '../../lib/games'
import { type ServerInstance, type ModEntry } from '../../lib/instances'
import { mockApi } from '../setup'

const minecraftGame = GAMES.find(g => g.id === 'minecraft')!
const valheimGame = GAMES.find(g => g.id === 'valheim')!
const palworldGame = GAMES.find(g => g.id === 'palworld')!

const instance: ServerInstance = {
  id: 'mc-mods-1',
  gameId: 'minecraft',
  name: 'Mod Server',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

const sampleMods: ModEntry[] = [
  { filename: 'JEI-1.20.jar', name: 'Just Enough Items', gameId: 'minecraft', size: 409_600, addedAt: Date.now() },
  { filename: 'Waystones-1.20.jar', name: 'Waystones', gameId: 'minecraft', size: 204_800, addedAt: Date.now() },
]

const onInstanceUpdated = vi.fn()

function renderMods(game = minecraftGame, inst = instance) {
  return render(<ModsPanel game={game} instance={inst} onInstanceUpdated={onInstanceUpdated} />)
}

describe('ModsPanel — empty state', () => {
  it('shows empty state when library is empty', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods()
    await waitFor(() => {
      expect(screen.getByText(/No mods in library yet/i)).toBeInTheDocument()
    })
  })

  it('shows correct mod count in header (0)', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods()
    await waitFor(() => {
      expect(screen.getByText(/0 mods installed/i)).toBeInTheDocument()
    })
  })

  it('calls listMods on mount with the correct gameId', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods()
    await waitFor(() => {
      expect(mockApi.listMods).toHaveBeenCalledWith('minecraft')
    })
  })
})

describe('ModsPanel — drop zone', () => {
  it('shows .jar in the drop zone for Minecraft', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods()
    await waitFor(() => {
      expect(screen.getByText(/.jar/i)).toBeInTheDocument()
    })
  })

  it('shows .pak in the drop zone for Palworld', async () => {
    mockApi.listMods.mockResolvedValue([])
    const palInst = { ...instance, gameId: 'palworld' }
    renderMods(palworldGame, palInst)
    await waitFor(() => {
      expect(screen.getByText(/.pak/i)).toBeInTheDocument()
    })
  })

  it('shows .dll and .zip in the drop zone for Valheim', async () => {
    mockApi.listMods.mockResolvedValue([])
    const valInst = { ...instance, gameId: 'valheim' }
    renderMods(valheimGame, valInst)
    await waitFor(() => {
      // Match the combined drop zone text to be unambiguous
      expect(screen.getByText(/Drop .dll, .zip files/i)).toBeInTheDocument()
    })
  })
})

describe('ModsPanel — library with mods', () => {
  it('renders each mod name', async () => {
    mockApi.listMods.mockResolvedValue(sampleMods)
    renderMods()
    await waitFor(() => {
      expect(screen.getByText('Just Enough Items')).toBeInTheDocument()
      expect(screen.getByText('Waystones')).toBeInTheDocument()
    })
  })

  it('shows mod count in header', async () => {
    mockApi.listMods.mockResolvedValue(sampleMods)
    renderMods()
    await waitFor(() => {
      expect(screen.getByText(/2 mods installed/i)).toBeInTheDocument()
    })
  })

  it('shows file size in KB', async () => {
    mockApi.listMods.mockResolvedValue(sampleMods)
    renderMods()
    await waitFor(() => {
      expect(screen.getByText(/400 KB/)).toBeInTheDocument()
    })
  })

  it('shows "Enabled" badge for enabled mods', async () => {
    mockApi.listMods.mockResolvedValue(sampleMods)
    const instanceWithMod = { ...instance, enabledMods: ['JEI-1.20.jar'] }
    renderMods(minecraftGame, instanceWithMod)
    await waitFor(() => {
      expect(screen.getByText('Enabled')).toBeInTheDocument()
    })
  })

  it('calls setEnabledMods and onInstanceUpdated when a toggle is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listMods.mockResolvedValue([sampleMods[0]])
    mockApi.setEnabledMods.mockResolvedValue(undefined)
    renderMods()
    await waitFor(() => screen.getByText('Just Enough Items'))
    // Find the toggle button (rounded-full)
    const toggles = document.querySelectorAll('button.rounded-full')
    await user.click(toggles[0])
    expect(mockApi.setEnabledMods).toHaveBeenCalledWith(
      instance.id,
      'minecraft',
      ['JEI-1.20.jar']
    )
    expect(onInstanceUpdated).toHaveBeenCalledWith(
      expect.objectContaining({ enabledMods: ['JEI-1.20.jar'] })
    )
  })

  it('calls removeMod when the trash icon is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listMods.mockResolvedValue([sampleMods[0]])
    mockApi.removeMod.mockResolvedValue(undefined)
    renderMods()
    await waitFor(() => screen.getByText('Just Enough Items'))
    // Trash button is inside a group — hover to reveal, then click
    const trashButton = document.querySelector('button.opacity-0') as HTMLButtonElement
    // Override opacity so it's clickable in tests
    if (trashButton) {
      trashButton.style.opacity = '1'
      await user.click(trashButton)
      expect(mockApi.removeMod).toHaveBeenCalledWith('minecraft', 'JEI-1.20.jar')
    }
  })
})

describe('ModsPanel — BepInEx export', () => {
  it('shows Share Mod Pack card for Valheim', async () => {
    mockApi.listMods.mockResolvedValue([])
    const valInst = { ...instance, gameId: 'valheim' }
    renderMods(valheimGame, valInst)
    await waitFor(() => {
      expect(screen.getByText(/Share Mod Pack/i)).toBeInTheDocument()
    })
  })

  it('does NOT show Share Mod Pack card for Minecraft', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods(minecraftGame, instance)
    await waitFor(() => {
      expect(screen.queryByText(/Share Mod Pack/i)).not.toBeInTheDocument()
    })
  })

  it('calls exportBepInEx when Export .zip is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listMods.mockResolvedValue([])
    const valInst = { ...instance, gameId: 'valheim', name: 'Nordic Server' }
    renderMods(valheimGame, valInst)
    await waitFor(() => screen.getByRole('button', { name: /Export .zip/i }))
    await user.click(screen.getByRole('button', { name: /Export .zip/i }))
    expect(mockApi.exportBepInEx).toHaveBeenCalledWith('valheim', instance.id, 'Nordic Server')
  })

  it('shows Browse button for opening file picker', async () => {
    mockApi.listMods.mockResolvedValue([])
    renderMods()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Browse/i })).toBeInTheDocument()
    })
  })

  it('calls openModPicker when Browse is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listMods.mockResolvedValue([])
    mockApi.openModPicker.mockResolvedValue([])
    renderMods()
    await waitFor(() => screen.getByRole('button', { name: /Browse/i }))
    await user.click(screen.getByRole('button', { name: /Browse/i }))
    expect(mockApi.openModPicker).toHaveBeenCalledWith('minecraft')
  })

  it('shows modsNote for Valheim', async () => {
    mockApi.listMods.mockResolvedValue([])
    const valInst = { ...instance, gameId: 'valheim' }
    renderMods(valheimGame, valInst)
    await waitFor(() => {
      // Match the specific modsNote warning text (distinct from the Share Mod Pack card)
      expect(screen.getByText(/Requires BepInEx installed/i)).toBeInTheDocument()
    })
  })
})
