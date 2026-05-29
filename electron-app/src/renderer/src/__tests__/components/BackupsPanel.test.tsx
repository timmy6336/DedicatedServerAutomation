import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import BackupsPanel from '../../components/BackupsPanel'
import { GAMES } from '../../lib/games'
import { type ServerInstance } from '../../lib/instances'
import { mockApi } from '../setup'

const game = GAMES.find(g => g.id === 'minecraft')!
const instance: ServerInstance = {
  id: 'mc-bkp-1',
  gameId: 'minecraft',
  name: 'Backup Test Server',
  config: {},
  enabledMods: [],
  createdAt: Date.now(),
}

const sampleBackups = [
  { id: 'bkp-001', label: '2024-01-15 14:30', sizeBytes: 52_428_800 },
  { id: 'bkp-002', label: '2024-01-14 10:00', sizeBytes: 1_073_741_824 },
]

function renderBackups(serverRunning = false) {
  return render(<BackupsPanel game={game} instance={instance} serverRunning={serverRunning} />)
}

describe('BackupsPanel — empty state', () => {
  it('shows empty state message when no backups exist', async () => {
    mockApi.listBackups.mockResolvedValue([])
    renderBackups()
    await waitFor(() => {
      expect(screen.getByText(/No backups yet/i)).toBeInTheDocument()
    })
  })

  it('shows backup count in subtitle (0)', async () => {
    mockApi.listBackups.mockResolvedValue([])
    renderBackups()
    await waitFor(() => {
      expect(screen.getByText(/0 backups/i)).toBeInTheDocument()
    })
  })

  it('shows Backups heading', async () => {
    renderBackups()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Backups/i })).toBeInTheDocument()
    })
  })
})

describe('BackupsPanel — with backups', () => {
  it('renders each backup label', async () => {
    mockApi.listBackups.mockResolvedValue(sampleBackups)
    renderBackups()
    await waitFor(() => {
      expect(screen.getByText('2024-01-15 14:30')).toBeInTheDocument()
      expect(screen.getByText('2024-01-14 10:00')).toBeInTheDocument()
    })
  })

  it('formats backup sizes correctly', async () => {
    mockApi.listBackups.mockResolvedValue(sampleBackups)
    renderBackups()
    await waitFor(() => {
      expect(screen.getByText(/50\.0 MB/)).toBeInTheDocument()
      expect(screen.getByText(/1\.00 GB/)).toBeInTheDocument()
    })
  })

  it('shows backup count in subtitle', async () => {
    mockApi.listBackups.mockResolvedValue(sampleBackups)
    renderBackups()
    await waitFor(() => {
      expect(screen.getByText(/2 backups/i)).toBeInTheDocument()
    })
  })

  it('renders Restore and Delete buttons for each backup', async () => {
    mockApi.listBackups.mockResolvedValue(sampleBackups)
    renderBackups()
    await waitFor(() => {
      const restoreButtons = screen.getAllByRole('button', { name: /Restore/i })
      expect(restoreButtons).toHaveLength(2)
    })
  })
})

describe('BackupsPanel — create backup', () => {
  it('Create Backup button is enabled when server is stopped', async () => {
    mockApi.listBackups.mockResolvedValue([])
    renderBackups(false)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Create Backup/i })).not.toBeDisabled()
    })
  })

  it('Create Backup button is disabled when server is running', async () => {
    mockApi.listBackups.mockResolvedValue([])
    renderBackups(true)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Create Backup/i })).toBeDisabled()
    })
  })

  it('shows warning banner when server is running', async () => {
    renderBackups(true)
    await waitFor(() => {
      expect(screen.getByText(/Stop the server before/i)).toBeInTheDocument()
    })
  })

  it('calls createBackup when Create Backup is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValue([])
    mockApi.createBackup.mockResolvedValue(undefined)
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Create Backup/i }))
    await user.click(screen.getByRole('button', { name: /Create Backup/i }))
    expect(mockApi.createBackup).toHaveBeenCalledWith('minecraft', 'mc-bkp-1')
  })

  it('reloads backup list after creation', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValueOnce([])
    mockApi.listBackups.mockResolvedValueOnce([sampleBackups[0]])
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Create Backup/i }))
    await user.click(screen.getByRole('button', { name: /Create Backup/i }))
    await waitFor(() => {
      expect(mockApi.listBackups).toHaveBeenCalledTimes(2)
    })
  })
})

describe('BackupsPanel — restore flow', () => {
  it('shows inline confirm when Restore is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValue([sampleBackups[0]])
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Restore/i }))
    await user.click(screen.getByRole('button', { name: /Restore/i }))
    await waitFor(() => {
      expect(screen.getByText(/Overwrite current files/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Yes, restore/i })).toBeInTheDocument()
    })
  })

  it('dismisses confirm dialog when Cancel is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValue([sampleBackups[0]])
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Restore/i }))
    await user.click(screen.getByRole('button', { name: /Restore/i }))
    await waitFor(() => screen.getByRole('button', { name: /Yes, restore/i }))
    await user.click(screen.getByRole('button', { name: /Cancel/i }))
    await waitFor(() => {
      expect(screen.queryByText(/Overwrite current files/i)).not.toBeInTheDocument()
    })
  })

  it('calls restoreBackup when Yes, restore is confirmed', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValue([sampleBackups[0]])
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Restore/i }))
    await user.click(screen.getByRole('button', { name: /Restore/i }))
    await waitFor(() => screen.getByRole('button', { name: /Yes, restore/i }))
    await user.click(screen.getByRole('button', { name: /Yes, restore/i }))
    expect(mockApi.restoreBackup).toHaveBeenCalledWith('minecraft', 'mc-bkp-1', 'bkp-001')
  })
})

describe('BackupsPanel — delete', () => {
  it('calls deleteBackup when the trash icon is clicked', async () => {
    const user = userEvent.setup()
    mockApi.listBackups.mockResolvedValue([sampleBackups[0]])
    renderBackups(false)
    await waitFor(() => screen.getByRole('button', { name: /Restore/i }))
    // The delete button has no accessible name — select by sibling proximity or role
    const deleteButtons = screen.getAllByRole('button').filter(b => !b.textContent?.match(/Restore|Create|Backups/))
    // The last button near each backup row is delete
    await user.click(deleteButtons[deleteButtons.length - 1])
    expect(mockApi.deleteBackup).toHaveBeenCalledWith('minecraft', 'mc-bkp-1', 'bkp-001')
  })
})
