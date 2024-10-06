check:
	mypy ./setup.py
	mypy ./substitute.py
	printf "Types are sound\n"
