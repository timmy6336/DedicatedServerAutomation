import { contextBridge, ipcRenderer } from 'electron'

const api = {
  // Window controls
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close:    () => ipcRenderer.send('window:close'),

  // Instance management
  listInstances:    (gameId: string) =>
    ipcRenderer.invoke('instance:list', gameId),
  createInstance:   (gameId: string, name: string) =>
    ipcRenderer.invoke('instance:create', gameId, name),
  deleteInstance:   (instanceId: string, gameId: string) =>
    ipcRenderer.invoke('instance:delete', instanceId, gameId),
  renameInstance:   (instanceId: string, name: string) =>
    ipcRenderer.invoke('instance:rename', instanceId, name),
  saveConfig:       (instanceId: string, config: Record<string, unknown>) =>
    ipcRenderer.invoke('instance:saveConfig', instanceId, config),
  loadConfig:       (instanceId: string) =>
    ipcRenderer.invoke('instance:loadConfig', instanceId),
  setEnabledMods:   (instanceId: string, gameId: string, enabledMods: string[]) =>
    ipcRenderer.invoke('instance:setEnabledMods', instanceId, gameId, enabledMods),

  // Server state
  isInstalled: (gameId: string, instanceId: string, subdir: string, exe: string) =>
    ipcRenderer.invoke('server:isInstalled', gameId, instanceId, subdir, exe),
  isRunning:   (instanceId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:isRunning', instanceId, processNames),
  getLocalIp:  () => ipcRenderer.invoke('server:localIp'),
  checkJava:   (): Promise<string | null> => ipcRenderer.invoke('server:checkJava'),

  // Install
  startInstall: (gameId: string, instanceId: string, steamAppId: string, installMode: string) =>
    ipcRenderer.invoke('install:start', gameId, instanceId, steamAppId, installMode),

  // Server lifecycle
  startServer: (instanceId: string, gameId: string, launchMode: string, exeRelPath: string, args: string[]) =>
    ipcRenderer.invoke('server:start', instanceId, gameId, launchMode, exeRelPath, args),
  stopServer:  (instanceId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:stop', instanceId, processNames),

  // Mod library
  listMods:    (gameId: string) => ipcRenderer.invoke('mods:list', gameId),
  addMods:     (gameId: string, paths: string[]) => ipcRenderer.invoke('mods:add', gameId, paths),
  removeMod:   (gameId: string, filename: string) => ipcRenderer.invoke('mods:remove', gameId, filename),
  openModPicker: (gameId: string) => ipcRenderer.invoke('mods:openPicker', gameId),

  // Backups
  createBackup:  (gameId: string, instanceId: string) =>
    ipcRenderer.invoke('backup:create', gameId, instanceId),
  listBackups:   (gameId: string, instanceId: string) =>
    ipcRenderer.invoke('backup:list', gameId, instanceId),
  restoreBackup: (gameId: string, instanceId: string, bkpId: string) =>
    ipcRenderer.invoke('backup:restore', gameId, instanceId, bkpId),
  deleteBackup:  (gameId: string, instanceId: string, bkpId: string) =>
    ipcRenderer.invoke('backup:delete', gameId, instanceId, bkpId),

  // Event listeners
  on: (channel: string, fn: (...args: unknown[]) => void) => {
    const wrapped = (_: Electron.IpcRendererEvent, ...args: unknown[]) => fn(...args)
    ipcRenderer.on(channel, wrapped)
    return () => ipcRenderer.removeListener(channel, wrapped)
  }
}

contextBridge.exposeInMainWorld('api', api)

export type ElectronAPI = typeof api
