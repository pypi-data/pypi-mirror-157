# Amazon EFS (amazon-efs)

Amazon EFS (amazon-efs) allows programmatically manipulate EFS data (create, read, delete, list files) from any machine.

# Prerequisites
* python
* pip
* boto3  
* AWS Account
* AWS Credentials

# Install
pip install amazon-efs

# Warning
EFS should have at least one mount target in a Private subnet

# Limits
*list_files*, *upload*, *download*, *delete* actions are limited by 15 minutes execution time (AWS Lambda works under the hood)

# Basics

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

# Deploying required underlying resources
efs.init()
# Actions (e.g. list_files, upload, download, delete)
files_list = efs.list_files()
# Don't forget to destroy underlying resources at the end of the session
efs.destroy()

```

# Actions

## List files

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

efs.init()

files_list = efs.list_files()
print(files_list)
files_list = efs.list_files('dir1')
print(files_list)
files_list = efs.list_files('dir1/dir2')
print(files_list)

efs.destroy()
```

## Upload
```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

efs.init()

efs.upload('file.txt')
efs.upload('file.txt', 'dir1/new_file.txt')
efs.upload('file.txt', 'dir1/dir2/new_file.txt')
efs.upload('file.txt', 'dir1/dir3/new_file.txt')
efs.upload('file.txt', 'dir2/dir3/new_file.txt')
efs.upload('file.txt', 'dir2/dir4/new_file.txt')

efs.destroy()
```

## Download
```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

efs.init()

efs.download('dir1/dir3/new_file.txt', 'file1.txt')

efs.destroy()
```

## Delete

### Delete file

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

efs.init()

efs.delete('dir2/dir3/new_file.txt')

efs.destroy()
```

### Delete folder

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

efs.init()

efs.delete('dir1/dir2/*')
efs.delete('dir1/*')

efs.destroy()
```

# State

You can destroy underlying infrastructure even after destroying EFS object from RAM if you saved the **state**

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id)

state = efs.init()

# Destroy object
del efs

efs = Efs(efs_id, { 'state': state })

files_list = efs.list_files()
print(files_list)

efs.destroy()
```

# Tags

You can add custom tags to underlying resources

```
from amazon_efs import Efs

efs_id = 'fs-0d74736bfc*******'
efs = Efs(efs_id, {
    'tags': {
        'k1': 'v1',
        'k2': 'v2'
    }
})

efs.init()

files_list = efs.list_files()
print(files_list)

efs.destroy()
```
