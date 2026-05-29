import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import NewServerModal from '../../components/NewServerModal'
import { GAMES } from '../../lib/games'
import { mockApi } from '../setup'

const game = GAMES.find(g => g.id === 'minecraft')!
const onCreated = vi.fn()
const onClose = vi.fn()

function renderModal() {
  return render(<NewServerModal game={game} onCreated={onCreated} onClose={onClose} />)
}

describe('NewServerModal', () => {
  it('shows the game name in the title', () => {
    renderModal()
    expect(screen.getByText(/New Minecraft Server/i)).toBeInTheDocument()
  })

  it('Create Server button is disabled when the name is empty', () => {
    renderModal()
    const btn = screen.getByRole('button', { name: /Create Server/i })
    expect(btn).toBeDisabled()
  })

  it('Create Server button is enabled after typing a name', async () => {
    const user = userEvent.setup()
    renderModal()
    const input = screen.getByRole('textbox')
    await user.type(input, 'My Server')
    const btn = screen.getByRole('button', { name: /Create Server/i })
    expect(btn).not.toBeDisabled()
  })

  it('calls onClose when Cancel is clicked', async () => {
    const user = userEvent.setup()
    renderModal()
    await user.click(screen.getByRole('button', { name: /Cancel/i }))
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('calls createInstance and onCreated when the form is submitted', async () => {
    const user = userEvent.setup()
    renderModal()
    await user.type(screen.getByRole('textbox'), 'Survival World')
    await user.click(screen.getByRole('button', { name: /Create Server/i }))
    expect(mockApi.createInstance).toHaveBeenCalledWith('minecraft', 'Survival World')
    expect(onCreated).toHaveBeenCalled()
  })

  it('submits on Enter key', async () => {
    const user = userEvent.setup()
    renderModal()
    const input = screen.getByRole('textbox')
    await user.type(input, 'Press Enter{Enter}')
    expect(mockApi.createInstance).toHaveBeenCalledWith('minecraft', 'Press Enter')
  })

  it('trims whitespace before creating', async () => {
    const user = userEvent.setup()
    renderModal()
    await user.type(screen.getByRole('textbox'), '  Trimmed Name  ')
    await user.click(screen.getByRole('button', { name: /Create Server/i }))
    expect(mockApi.createInstance).toHaveBeenCalledWith('minecraft', 'Trimmed Name')
  })
})
