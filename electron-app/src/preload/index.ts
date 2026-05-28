import { contextBridge, ipcRenderer } from 'electron'

const api = {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close:    () => ipcRenderer.send('window:close'),

  // Config
  loadConfig: (gameId: string) => ipcRenderer.invoke('config:load', gameId),
  saveConfig: (gameId: string, config: Record<string, unknown>) =>
    ipcRenderer.invoke('config:save', gameId, config),

  // Server state
  isInstalled: (gameId: string, subdir: string, exe: string) =>
    ipcRenderer.invoke('server:isInstalled', gameId, subdir, exe),
  isRunning: (processNames: string[]) =>
    ipcRenderer.invoke('server:isRunning', processNames),
  getLocalIp: () => ipcRenderer.invoke('server:localIp'),

  // Install flow
  startInstall: (gameId: string, steamAppId: string) =>
    ipcRenderer.invoke('install:start', gameId, steamAppId),

  // Server lifecycle
  startServer: (gameId: string, exePath: string, args: string[]) =>
    ipcRenderer.invoke('server:start', gameId, exePath, args),
  stopServer: (gameId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:stop', gameId, processNames),

  // Event listeners
  on: (channel: string, fn: (...args: unknown[]) => void) => {
    const wrapped = (_: Electron.IpcRendererEvent, ...args: unknown[]) => fn(...args)
    ipcRenderer.on(channel, wrapped)
    return () => ipcRenderer.removeListener(channel, wrapped)
  }
}

contextBridge.exposeInMainWorld('api', api)

export type ElectronAPI = typeof api
