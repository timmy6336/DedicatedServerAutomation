import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TitleBar from '../../components/TitleBar'
import { mockApi } from '../setup'

describe('TitleBar', () => {
  it('renders the app name', () => {
    render(<TitleBar />)
    expect(screen.getByText(/Server Manager/i)).toBeInTheDocument()
  })

  it('renders minimize, maximize, and close buttons', () => {
    const { container } = render(<TitleBar />)
    // Three buttons in the window controls area
    const buttons = container.querySelectorAll('button')
    expect(buttons).toHaveLength(3)
  })

  it('calls window.api.minimize when minimize button is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(<TitleBar />)
    const buttons = container.querySelectorAll('button')
    await user.click(buttons[0])
    expect(mockApi.minimize).toHaveBeenCalledOnce()
  })

  it('calls window.api.maximize when maximize button is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(<TitleBar />)
    const buttons = container.querySelectorAll('button')
    await user.click(buttons[1])
    expect(mockApi.maximize).toHaveBeenCalledOnce()
  })

  it('calls window.api.close when close button is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(<TitleBar />)
    const buttons = container.querySelectorAll('button')
    await user.click(buttons[2])
    expect(mockApi.close).toHaveBeenCalledOnce()
  })
})
