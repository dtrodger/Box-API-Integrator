FROM python:3.7

WORKDIR /home/bc_agent_queue_admin
ENV PYTHONPATH "${PYTHONPATH}:/home/bc_agent_queue_admin"

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN groupadd bc_agent_queue_admin_group && \
    useradd -m -g bc_agent_queue_admin_group -s /bin/bash bc_agent_queue_admin && \
    touch /home/bc_agent_queue_admin/data/log/bc_agent_queue_admin.info.log && \
    touch /home/bc_agent_queue_admin/data/log/bc_agent_queue_admin.error.log && \
    chown -R bc_agent_queue_admin:bc_agent_queue_admin_group /home/bc_agent_queue_admin

USER bc_agent_queue_admin
CMD ["python", "bc_agent/cli", "queue-admin", "-c", "dev_docker"]
