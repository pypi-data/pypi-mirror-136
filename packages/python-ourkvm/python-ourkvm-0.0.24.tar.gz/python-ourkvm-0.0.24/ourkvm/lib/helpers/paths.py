import os
import re
import unicodedata

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = (
	"CON",
	"AUX",
	"COM1",
	"COM2",
	"COM3",
	"COM4",
	"LPT1",
	"LPT2",
	"LPT3",
	"PRN",
	"NUL",
)

def secure_filename(filename: str) -> str:
	"""
	Attempts to secure a given filename, not a path.
	It excludes any characters that could be harmful to a path.
	This function should not be used on paths.
	"""
	filename = unicodedata.normalize("NFKD", filename)
	filename = filename.encode("ascii", "ignore").decode("ascii")

	for sep in os.path.sep, os.path.altsep:
		if sep:
			filename = filename.replace(sep, " ")
	
	filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
		"._"
	)

	if (
		os.name == "nt"
		and filename
		and filename.split(".")[0].upper() in _windows_device_files
	):
		filename = f"_{filename}"

	return filename