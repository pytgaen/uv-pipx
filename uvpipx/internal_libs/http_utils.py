# import urllib.request


# def download_file(
#     url,
#     destination_filename,
#     cafile=None,
# ) -> None:
#     if url.startswith("file:/"):
#         msg = "Download from file is not allowed !"
#         raise RuntimeError(msg)

#     with urllib.request.urlopen(url, cafile=cafile) as response, destination_filename.open(  # nosec: B310
#          "wb",
#     ) as file:
#         data = response.read(64 * 1024)
#         while data:
#             file.write(data)
#             data = response.read(64 * 1024)
#         file.write(data)


# def download_as_bytes(
#     url,
#     destination_filename,
#     cafile=None,
# ):
#     if url.startswith("file:/"):
#         msg = "Download from file is not allowed !"
#         raise RuntimeError(msg)

#     with urllib.request.urlopen(url, cafile=cafile) as response:  # nosec: B310
#         data = response.read(64 * 1024)
#         while data:
#             data += response.read(64 * 1024)

#     return data
