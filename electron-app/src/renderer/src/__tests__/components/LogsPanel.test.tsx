import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LogsPanel from '../../components/LogsPanel'
import { mockApi } from '../setup'

function renderLogsPanel(serverRunning = false, instanceId = 'test-inst-1') {
  return render(<LogsPanel instanceId={instanceId} serverRunning={serverRunning} />)
}

describe('LogsPanel — empty state', () => {
  it('shows idle message when server is not running', () => {
    renderLogsPanel(false)
    expect(screen.getByText(/No log output yet/i)).toBeInTheDocument()
  })

  it('shows waiting message when server is running but no output yet', () => {
    renderLogsPanel(true)
    // When running with no output yet, shows "Waiting for output…"
    expect(screen.getByText(/Waiting for output/i)).toBeInTheDocument()
  })

  it('Clear button is disabled when there are no logs', () => {
    renderLogsPanel()
    const clearBtn = screen.getByRole('button', { name: /Clear/i })
    expect(clearBtn).toBeDisabled()
  })

  it('shows "Server Log" heading', () => {
    renderLogsPanel()
    expect(screen.getByText(/Server Log/i)).toBeInTheDocument()
  })

  it('registers event listener on mount', () => {
    renderLogsPanel()
    expect(mockApi.on).toHaveBeenCalledWith('server:log', expect.any(Function))
  })

  it('unsubscribes from events on unmount', () => {
    const unsubscribe = vi.fn()
    mockApi.on.mockReturnValue(unsubscribe)
    const { unmount } = renderLogsPanel()
    unmount()
    expect(unsubscribe).toHaveBeenCalled()
  })
})

describe('LogsPanel — with log lines', () => {
  it('renders log lines as they arrive via server:log events', async () => {
    let logHandler: ((data: unknown) => void) | undefined

    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'server:log') logHandler = fn as (d: unknown) => void
      return vi.fn()
    })

    renderLogsPanel(true, 'inst-abc')

    logHandler?.({ instanceId: 'inst-abc', line: '[INFO] Server started on port 25565' })
    logHandler?.({ instanceId: 'inst-abc', line: '[WARN] Low memory detected' })

    await waitFor(() => {
      expect(screen.getByText(/Server started on port 25565/i)).toBeInTheDocument()
      expect(screen.getByText(/Low memory detected/i)).toBeInTheDocument()
    })
  })

  it('ignores log lines from a different instanceId', async () => {
    let logHandler: ((data: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'server:log') logHandler = fn as (d: unknown) => void
      return vi.fn()
    })

    renderLogsPanel(true, 'my-instance')
    logHandler?.({ instanceId: 'other-instance', line: 'Should be ignored' })

    await waitFor(() => {
      expect(screen.queryByText('Should be ignored')).not.toBeInTheDocument()
    })
  })

  it('clears all lines when Clear button is clicked', async () => {
    const user = userEvent.setup()
    let logHandler: ((data: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'server:log') logHandler = fn as (d: unknown) => void
      return vi.fn()
    })

    renderLogsPanel(true, 'clear-test')
    logHandler?.({ instanceId: 'clear-test', line: 'Some log line' })
    await waitFor(() => screen.getByText('Some log line'))

    await user.click(screen.getByRole('button', { name: /Clear/i }))

    await waitFor(() => {
      expect(screen.queryByText('Some log line')).not.toBeInTheDocument()
    })
  })

  it('resets log lines when instanceId changes', async () => {
    let logHandler: ((data: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'server:log') logHandler = fn as (d: unknown) => void
      return vi.fn()
    })

    const { rerender } = render(<LogsPanel instanceId="inst-A" serverRunning={true} />)
    logHandler?.({ instanceId: 'inst-A', line: 'Line from A' })
    await waitFor(() => screen.getByText('Line from A'))

    rerender(<LogsPanel instanceId="inst-B" serverRunning={true} />)
    await waitFor(() => {
      expect(screen.queryByText('Line from A')).not.toBeInTheDocument()
    })
  })
})

describe('LogsPanel — subtitle text', () => {
  it('shows line count when server is running', async () => {
    let logHandler: ((data: unknown) => void) | undefined
    mockApi.on.mockImplementation((channel: string, fn: (...args: unknown[]) => void) => {
      if (channel === 'server:log') logHandler = fn as (d: unknown) => void
      return vi.fn()
    })

    renderLogsPanel(true, 'cnt-inst')
    logHandler?.({ instanceId: 'cnt-inst', line: 'Line 1' })
    logHandler?.({ instanceId: 'cnt-inst', line: 'Line 2' })
    logHandler?.({ instanceId: 'cnt-inst', line: 'Line 3' })

    await waitFor(() => {
      expect(screen.getByText(/3 lines/i)).toBeInTheDocument()
    })
  })
})
