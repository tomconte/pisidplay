import os
import signal
import web

hvsc_root = '/home/pi/C64Music'
cur_pid = 0

urls = (
  "/", "main",
  "/dir/(.*)", "dir",
  "/play/(.+)", "play"
)

app = web.application(urls, globals())
render = web.template.render('templates', globals={'os': os})

class main:
  def GET(self):
    return "Hello world!"

class dir:
  def GET(self, dir):

    curdir = os.path.join(hvsc_root, dir)
    dirlist = os.listdir(curdir)

    dirs = []
    files = []

    for f in dirlist:
      if os.path.isdir(os.path.join(curdir, f)):
        dirs.append(os.path.join(dir, f))
      if os.path.isfile(os.path.join(curdir, f)):
        files.append(os.path.join(dir, f))
    
    dirs.sort()
    files.sort()
    
    return render.dir(dirs, files)

class play:
  def GET(self, file):
    global cur_pid
    if cur_pid != 0:
      os.kill(cur_pid, signal.SIGINT)
    cur_pid = os.spawnlp(os.P_NOWAIT, 'sidplay2', 'sidplay2', os.path.join(hvsc_root, file))
    return render.play(file)

if __name__ == "__main__":
  app.run()
