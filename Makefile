help:
	@echo
	@echo
	@echo "  -----------------------------------------------------------------------------------------------------------"
	@echo "  Box Consulting Python process manager Makefile"
	@echo "  -----------------------------------------------------------------------------------------------------------"
	@echo "  dev"
	@echo "  prod"
	@echo
	@echo

dev:
	docker-compose -f docker-compose.dev.yml up --build

prod:
	docker-compose up --build