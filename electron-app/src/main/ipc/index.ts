import { ipcMain, BrowserWindow, app } from 'electron'
import { spawnSync, spawn, ChildProcess } from 'child_process'
import { existsSync, mkdirSync, createWriteStream } from 'fs'
import { join } from 'path'
import { get as httpGet } from 'https'
import { readFile, writeFile } from 'fs/promises'
import * as os from 'os'

// ── active server processes keyed by game id ────────────────────────────────
const runningProcesses = new Map<string, ChildProcess>()

// ── persistent config store ─────────────────────────────────────────────────
const configPath = join(app.getPath('userData'), 'server-configs.json')

async function readConfigs(): Promise<Record<string, Record<string, unknown>>> {
  try {
    const raw = await readFile(configPath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

async function writeConfigs(data: Record<string, Record<string, unknown>>): Promise<void> {
  await writeFile(configPath, JSON.stringify(data, null, 2), 'utf-8')
}

// ── install directory ────────────────────────────────────────────────────────
function getInstallBase(): string {
  return join(app.getPath('userData'), 'servers')
}

function getSteamCmdPath(): string {
  const base = join(app.getPath('userData'), 'steamcmd')
  const exe = process.platform === 'win32' ? 'steamcmd.exe' : 'steamcmd.sh'
  return join(base, exe)
}

// ── download helper (streamed, with progress) ────────────────────────────────
function downloadFile(url: string, dest: string, onProgress: (pct: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    const dir = join(dest, '..')
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
    const file = createWriteStream(dest)
    httpGet(url, (res) => {
      const total = parseInt(res.headers['content-length'] || '0', 10)
      let received = 0
      res.on('data', (chunk: Buffer) => {
        received += chunk.length
        if (total > 0) onProgress(Math.round((received / total) * 100))
        file.write(chunk)
      })
      res.on('end', () => { file.end(); resolve() })
      res.on('error', reject)
    }).on('error', reject)
  })
}

// ── send event to all renderer windows ──────────────────────────────────────
function broadcast(channel: string, ...args: unknown[]): void {
  BrowserWindow.getAllWindows().forEach(w => w.webContents.send(channel, ...args))
}

// ── IPC registration ─────────────────────────────────────────────────────────
export function registerIpcHandlers(): void {

  // Window controls
  ipcMain.on('window:minimize', () => BrowserWindow.getFocusedWindow()?.minimize())
  ipcMain.on('window:maximize', () => {
    const win = BrowserWindow.getFocusedWindow()
    if (win?.isMaximized()) win.unmaximize()
    else win?.maximize()
  })
  ipcMain.on('window:close', () => BrowserWindow.getFocusedWindow()?.close())

  // Config persistence
  ipcMain.handle('config:load', async (_, gameId: string) => {
    const all = await readConfigs()
    return all[gameId] ?? null
  })

  ipcMain.handle('config:save', async (_, gameId: string, config: Record<string, unknown>) => {
    const all = await readConfigs()
    all[gameId] = config
    await writeConfigs(all)
    return true
  })

  // Check if game server is installed
  ipcMain.handle('server:isInstalled', (_, gameId: string, executableSubdir: string, executable: string) => {
    const base = join(getInstallBase(), gameId)
    const exePath = executableSubdir
      ? join(base, executableSubdir, executable)
      : join(base, executable)
    return existsSync(exePath)
  })

  // Check if server is running
  ipcMain.handle('server:isRunning', (_, processNames: string[]) => {
    for (const [, proc] of runningProcesses) {
      if (proc && !proc.killed) return true
    }
    // Fallback: check by name via tasklist/ps
    try {
      if (process.platform === 'win32') {
        const result = spawnSync('tasklist', ['/FO', 'CSV', '/NH'], { encoding: 'utf-8' })
        const lower = (result.stdout || '').toLowerCase()
        return processNames.some(n => lower.includes(n.toLowerCase()))
      } else {
        const result = spawnSync('pgrep', ['-f', processNames[0]], { encoding: 'utf-8' })
        return result.status === 0
      }
    } catch {
      return false
    }
  })

  // Get local IP
  ipcMain.handle('server:localIp', () => {
    const nets = os.networkInterfaces()
    for (const iface of Object.values(nets)) {
      for (const addr of iface ?? []) {
        if (addr.family === 'IPv4' && !addr.internal) return addr.address
      }
    }
    return '127.0.0.1'
  })

  // Install SteamCMD + game server (streamed progress via events)
  ipcMain.handle('install:start', async (_, gameId: string, steamAppId: string) => {
    const steamCmdPath = getSteamCmdPath()
    const installDir = join(getInstallBase(), gameId)

    if (!existsSync(join(steamCmdPath, '..'))) {
      mkdirSync(join(steamCmdPath, '..'), { recursive: true })
    }
    if (!existsSync(installDir)) mkdirSync(installDir, { recursive: true })

    // Step 1: Download SteamCMD
    if (!existsSync(steamCmdPath)) {
      broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: 0 })
      const url = process.platform === 'win32'
        ? 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
        : 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz'
      const archive = steamCmdPath.replace(/\.(exe|sh)$/, process.platform === 'win32' ? '.zip' : '.tar.gz')
      try {
        await downloadFile(url, archive, (pct) => {
          broadcast('install:step', { step: 0, label: 'Downloading SteamCMD…', progress: pct })
        })
        broadcast('install:step', { step: 0, label: 'Extracting SteamCMD…', progress: 100 })
        // Extract
        if (process.platform === 'win32') {
          spawnSync('powershell', ['-Command', `Expand-Archive -Path "${archive}" -DestinationPath "${join(steamCmdPath, '..')}" -Force`])
        } else {
          spawnSync('tar', ['-xzf', archive, '-C', join(steamCmdPath, '..')])
          spawnSync('chmod', ['+x', steamCmdPath])
        }
      } catch (e) {
        broadcast('install:error', String(e))
        return false
      }
    }

    // Step 2: Install game server via SteamCMD
    broadcast('install:step', { step: 1, label: 'Installing server files…', progress: 0 })
    return new Promise<boolean>((resolve) => {
      const args = [
        '+force_install_dir', installDir,
        '+login', 'anonymous',
        '+app_update', steamAppId, 'validate',
        '+quit'
      ]
      const proc = spawn(steamCmdPath, args)
      let outputBuffer = ''

      proc.stdout?.on('data', (chunk: Buffer) => {
        outputBuffer += chunk.toString()
        const lines = outputBuffer.split('\n')
        outputBuffer = lines.pop() ?? ''
        for (const line of lines) {
          broadcast('install:log', line)
          // Parse SteamCMD progress lines: "Update state (0x61) downloading, progress: 45.23 (1234 / 2345)"
          const match = line.match(/progress:\s*([\d.]+)/)
          if (match) {
            broadcast('install:step', {
              step: 1,
              label: 'Installing server files…',
              progress: Math.round(parseFloat(match[1]))
            })
          }
        }
      })

      proc.stderr?.on('data', (chunk: Buffer) => {
        broadcast('install:log', chunk.toString())
      })

      proc.on('close', (code) => {
        broadcast('install:step', { step: 1, label: 'Installation complete', progress: 100 })
        broadcast('install:done', code === 0)
        resolve(code === 0)
      })
    })
  })

  // Start server
  ipcMain.handle('server:start', (_, gameId: string, exePath: string, args: string[]) => {
    if (runningProcesses.get(gameId)?.killed === false) return true
    try {
      const proc = spawn(exePath, args, {
        cwd: join(exePath, '..'),
        detached: true,
        stdio: 'ignore'
      })
      proc.unref()
      runningProcesses.set(gameId, proc)
      return true
    } catch (e) {
      broadcast('server:error', String(e))
      return false
    }
  })

  // Stop server
  ipcMain.handle('server:stop', (_, gameId: string, processNames: string[]) => {
    const proc = runningProcesses.get(gameId)
    if (proc && !proc.killed) {
      proc.kill()
      runningProcesses.delete(gameId)
      return true
    }
    // Kill by name as fallback
    try {
      if (process.platform === 'win32') {
        for (const name of processNames) {
          spawnSync('taskkill', ['/F', '/IM', name])
        }
      } else {
        for (const name of processNames) {
          spawnSync('pkill', ['-f', name])
        }
      }
      return true
    } catch {
      return false
    }
  })
}
