# imgserv
A simple imgadm compatible image server for SmartOS.

This is a very dusty piece of code, having not been used for a long time. I also can't exactly guarantee that it's still protocol compliant - I know, for instance, that Joyent's client has fallen far behind docker's repo and I can't guarantee the same hasn't happened here.

But! If you're looking to distribute SmartOS images, you're probably in the right place :)

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
