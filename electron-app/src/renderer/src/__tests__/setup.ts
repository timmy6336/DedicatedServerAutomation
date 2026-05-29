import '@testing-library/jest-dom'
import { vi, afterEach } from 'vitest'

// Comprehensive mock of the Electron context-bridge API
export const mockApi = {
  // Window controls
  minimize: vi.fn(),
  maximize: vi.fn(),
  close: vi.fn(),

  // Instance management
  listInstances: vi.fn().mockResolvedValue([]),
  createInstance: vi.fn().mockResolvedValue({
    id: 'mock-instance-id',
    gameId: 'minecraft',
    name: 'Test Server',
    config: {},
    enabledMods: [],
    createdAt: Date.now(),
  }),
  deleteInstance: vi.fn().mockResolvedValue(undefined),
  renameInstance: vi.fn().mockResolvedValue(undefined),
  saveConfig: vi.fn().mockResolvedValue(undefined),
  loadConfig: vi.fn().mockResolvedValue(null),
  setEnabledMods: vi.fn().mockResolvedValue(undefined),

  // Server state
  isInstalled: vi.fn().mockResolvedValue(false),
  isRunning: vi.fn().mockResolvedValue(false),
  getLocalIp: vi.fn().mockResolvedValue('192.168.1.100'),
  checkJava: vi.fn().mockResolvedValue('17.0.12'),

  // Install
  startInstall: vi.fn().mockResolvedValue(undefined),
  cancelInstall: vi.fn().mockResolvedValue(undefined),

  // Server lifecycle
  startServer: vi.fn().mockResolvedValue(undefined),
  stopServer: vi.fn().mockResolvedValue(undefined),
  uninstallServer: vi.fn().mockResolvedValue(undefined),

  // Mod library
  listMods: vi.fn().mockResolvedValue([]),
  addMods: vi.fn().mockResolvedValue(undefined),
  removeMod: vi.fn().mockResolvedValue(undefined),
  openModPicker: vi.fn().mockResolvedValue([]),
  exportBepInEx: vi.fn().mockResolvedValue({ path: '/Users/test/mods.zip' }),

  // Backups
  createBackup: vi.fn().mockResolvedValue(undefined),
  listBackups: vi.fn().mockResolvedValue([]),
  restoreBackup: vi.fn().mockResolvedValue(undefined),
  deleteBackup: vi.fn().mockResolvedValue(undefined),

  // Event listeners — returns an unsubscribe function
  on: vi.fn().mockReturnValue(vi.fn()),
}

Object.defineProperty(window, 'api', {
  value: mockApi,
  writable: true,
})

afterEach(() => {
  vi.clearAllMocks()
  // Restore default return values after each test
  mockApi.listInstances.mockResolvedValue([])
  mockApi.loadConfig.mockResolvedValue(null)
  mockApi.isInstalled.mockResolvedValue(false)
  mockApi.isRunning.mockResolvedValue(false)
  mockApi.listMods.mockResolvedValue([])
  mockApi.listBackups.mockResolvedValue([])
  mockApi.on.mockReturnValue(vi.fn())
})
