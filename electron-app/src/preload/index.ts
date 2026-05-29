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
  isInstalled: (gameId: string, instanceId: string, installOnce: boolean, subdir: string, exe: string) =>
    ipcRenderer.invoke('server:isInstalled', gameId, instanceId, installOnce, subdir, exe),
  isRunning:   (instanceId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:isRunning', instanceId, processNames),
  getLocalIp:  () => ipcRenderer.invoke('server:localIp'),
  checkJava:   (): Promise<string | null> => ipcRenderer.invoke('server:checkJava'),

  // Install
  uninstallServer: (gameId: string, instanceId: string, installOnce: boolean) =>
    ipcRenderer.invoke('server:uninstall', gameId, instanceId, installOnce),
  startInstall: (gameId: string, instanceId: string, steamAppId: string, installMode: string, installOnce: boolean) =>
    ipcRenderer.invoke('install:start', gameId, instanceId, steamAppId, installMode, installOnce),
  cancelInstall: () => ipcRenderer.invoke('install:cancel'),

  // Server lifecycle
  startServer: (instanceId: string, gameId: string, launchMode: string, exeRelPath: string, args: string[], installOnce: boolean) =>
    ipcRenderer.invoke('server:start', instanceId, gameId, launchMode, exeRelPath, args, installOnce),
  stopServer:  (instanceId: string, processNames: string[]) =>
    ipcRenderer.invoke('server:stop', instanceId, processNames),

  // Mod library
  listMods:    (gameId: string) => ipcRenderer.invoke('mods:list', gameId),
  addMods:     (gameId: string, paths: string[]) => ipcRenderer.invoke('mods:add', gameId, paths),
  removeMod:   (gameId: string, filename: string) => ipcRenderer.invoke('mods:remove', gameId, filename),
  openModPicker:   (gameId: string) => ipcRenderer.invoke('mods:openPicker', gameId),
  exportBepInEx:   (gameId: string, instanceId: string, instanceName: string) =>
    ipcRenderer.invoke('mods:exportBepInEx', gameId, instanceId, instanceName),

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
