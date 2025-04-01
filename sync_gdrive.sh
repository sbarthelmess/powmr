#!/bin/bash
GDIR=/home/seb
GDATA=data.csv

# Cleanup mounts
fusermount -uq $GDIR/gdrive
# Mount Google Drive
rclone mount googledrive: $GDIR/gdrive -v --allow-non-empty --daemon
# Wait for Google Mount to complete
sleep 5
# Append uptime data to CSV
truncate -s -1 $GDIR/$GDATA
echo ", `uptime`" >> $GDIR/$GDATA
# Sync File to Google Drive
cp $GDIR/$GDATA $GDIR/gdrive/
sync
sleep 1
# Cleanup mount
fusermount -u $GDIR/gdrive
