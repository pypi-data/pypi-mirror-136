# pbx-lv2-records-uploader

Simple selectel upload

```python
    api = Uploader(Uploader.SERVICE_SELECTEL, {
        'username': 'user',
        'password': 'pass',
        'container': 'container_name'
    }, {
        'token_cache_dir': '/path/to/cache/dir'
    })

    uploadedFileUrl = api.upload(
        '/path/to/src/file', 'dst_folder/dst_filename')
        
    print(uploadedFileUrl)
```
