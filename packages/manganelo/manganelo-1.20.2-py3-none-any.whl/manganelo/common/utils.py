import os
import shutil
import locale
import typing
import datetime as dt
import html


def unescape_html(s: str) -> str:
	return html.unescape(s)


def split_at(s: str, sep: str) -> list[str]:
	return [x.strip() for x in s.split(sep)]


def save_image(image_data, path) -> typing.Union[str, None]:
	path = validate_path(path)

	with open(path, "wb") as fh:
		image_data.raw.decode_content = True

		# noinspection PyBroadException
		try:
			shutil.copyfileobj(image_data.raw, fh)

		except BaseException:
			return None

	return path


def parse_date(s: str, _format: str):

	try:
		locale.setlocale(locale.LC_ALL, "en_US.UTF8")

		return dt.datetime.strptime(s, _format)

	finally:
		locale.setlocale(locale.LC_ALL, '')


def validate_path(path: str):
	dir_, file = os.path.split(path)

	for char in ("\\", "/", ":", "*", "?", "<", ">", "|"):
		file = file.replace(char, "")

	return os.path.join(dir_, file)
