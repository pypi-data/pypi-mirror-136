# fsos

minio like python Local File System based Object Storage (FSOS)

## Usage

```
import fsos

fsos.make_bucket("my-bucket")
fsos.remove_bucket("my-bucket")
fsos.bucket_exists("my-bucket")
fsos.bucket_list()

fsos.put_filepath("my-bucket", "my-image.png", "/media/db/temp_file.png", {"cls" : [1]})
fsos.get_filepaths("my-bucket")

fsos.get_objects("my-bucket")
fsos.remove_object("my-bucket", "my-image.png")
```
