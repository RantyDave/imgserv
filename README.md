# imgserv
A simple imgadm compatible image server for SmartOS. Alarmingly reliable.

# howto
Run the Python in a directory. You can seed the directory with the zfs.bz2 and json files created as part of the [image production process](https://wiki.smartos.org/display/DOC/Managing+Images#ManagingImages-CreatingaCustomZoneImage).

To use it with a SmartOS client:
 *  Do `imgadm sources -e` to get to editing the image sources
 *  Append a line with your imagesource i.e. `http://my-image-server.20ft.nz:someport  imgapi`
 *  `imgadm avail` will now mix your images in with (eg) the Joyent ones
 *  To push an image it's just `imgadm publish -m <manifest> -f <file> http://my-image-server.20ft.nz:someport`
 
# further reading
 *  [imgadm man page](https://github.com/joyent/smartos-live/blob/master/src/img/man/imgadm.1m.md) on the actual SmartOS github page
 *  Reference material for [manifests](https://images.joyent.com/docs/#introduction)
 
Dead easy. Enjoy!
