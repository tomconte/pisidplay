import os
import subprocess
import json
import web
from azure.storage.common import CloudStorageAccount
from azure.storage.blob import BlobPrefix
from azure.storage.blob import ContentSettings

storage_account='hvsc'
storage_key='dgvR+Z3qoY0sRYjHfOkWDMG7oSrBjLoBgVE4DhAkaRtSjORjBajJc+ddWS4z47N9RV6JWg9UO5Bh0R5Xkek9Gw=='
storage_container='hvsc'

# Use sidplayfp on macOS, sidplay2 on Linux
if subprocess.check_output('uname').startswith('Darwin'):
  sid_player='sidplayfp'
else:
  sid_player='sidplay2'

urls = (
  "/", "main",
  "/dir/(.*)", "dir",
  "/play/(.+)", "play",
  "/convert/(.+)", "convert"
)

app = web.application(urls, globals())
render = web.template.render('templates', globals={'os': os})

storage_client = CloudStorageAccount(storage_account, storage_key)
blob_service = storage_client.create_block_blob_service()

class main:
  def GET(self):
    return "Hello world!"

class dir:
  def GET(self, dir):
    global blob_service

    # Workaround
    # https://github.com/Azure/azure-storage-python/issues/451

    if dir == '':
      bloblist = blob_service.list_blobs(storage_container, delimiter='/')
    else:
      bloblist = blob_service.list_blobs(storage_container, prefix=dir, delimiter='/')

    dirs = []
    files = []

    for f in bloblist:
      if isinstance(f, BlobPrefix):
        dirs.append(f.name)
      else:
        if f.name.endswith('.sid'):
          files.append(f.name)
    
    dirs.sort()
    files.sort()
    
    return render.dir(dirs, files)

class play:
  def GET(self, file):
    return render.play(file)

class convert:
  def GET(self, file):
    blob_path = os.path.dirname(file)
    sid_file = os.path.basename(file)
    wav_file = os.path.splitext(sid_file)[0] + ".wav"
    wav_blob = os.path.join(blob_path, wav_file)
    wav_url = blob_service.protocol + "://"  + blob_service.primary_endpoint+ "/" + storage_container + "/" + wav_blob
    # If the wav blob does not exist
    if not blob_service.exists(storage_container, wav_blob):
      # Download sid file from Blob Storage
      blob_service.get_blob_to_path(storage_container, file, sid_file)
      # Convert sid to wav
      print "Generating " + wav_file + " ..."
      retval = subprocess.call([sid_player, sid_player, '-w' + wav_file, sid_file])
      # TODO: check return value
      # Upload the wav file to 
      blob_service.create_blob_from_path(storage_container, wav_blob, wav_file,
        content_settings=ContentSettings(content_type='audio/wav'))
      # Delete the temp files: sid & wav
      # TODO: exceptions, race conditions etc.
      os.remove(sid_file)
      os.remove(wav_file)
    web.header("Location", wav_url)
    return wav_url

if __name__ == "__main__":
  app.run()
