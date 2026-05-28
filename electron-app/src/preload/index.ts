import { contextBridge, ipcRenderer } from 'electron'

const api = {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close:    () => ipcRenderer.send('window:close'),

  // Config
  loadConfig: (gameId: string) =>
    ipcRenderer.invoke('config:load', gameId),
  saveConfig: (gameId: string, config: Record<string, unknown>) =>
    ipcRenderer.invoke('config:save', gameId, config),

  // Server state
  isInstalled: (gameId: string, subdir: string, exe: string) =>
    ipcRenderer.invoke('server:isInstalled', gameId, subdir, exe),
  isRunning: (gameId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:isRunning', gameId, processNames),
  getLocalIp: () =>
    ipcRenderer.invoke('server:localIp'),
  checkJava: (): Promise<string | null> =>
    ipcRenderer.invoke('server:checkJava'),

  // Install — installMode: 'steam' | 'mojang'
  startInstall: (gameId: string, steamAppId: string, installMode: string) =>
    ipcRenderer.invoke('install:start', gameId, steamAppId, installMode),

  // Server lifecycle — launchMode passed so main knows how to spawn
  startServer: (gameId: string, exePath: string, args: string[], launchMode: string) =>
    ipcRenderer.invoke('server:start', gameId, exePath, args, launchMode),
  stopServer: (gameId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:stop', gameId, processNames),

  // Event listeners — returns unsubscribe fn
  on: (channel: string, fn: (...args: unknown[]) => void) => {
    const wrapped = (_: Electron.IpcRendererEvent, ...args: unknown[]) => fn(...args)
    ipcRenderer.on(channel, wrapped)
    return () => ipcRenderer.removeListener(channel, wrapped)
  }
}

contextBridge.exposeInMainWorld('api', api)

export type ElectronAPI = typeof api
