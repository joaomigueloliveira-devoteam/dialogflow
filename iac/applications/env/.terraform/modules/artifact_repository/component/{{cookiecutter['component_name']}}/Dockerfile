FROM {{cookiecutter.__tagged_base_image}}

{% if cookiecutter['entrypoint_format'] == "python" %}COPY requirements.txt .

RUN pip3 install keyrings.google-artifactregistry-auth==1.0.0
RUN pip3 install -r requirements.txt

COPY main.py .

ENTRYPOINT ["python", "main.py"]{% elif cookiecutter['entrypoint_format'] == "bash" %}RUN chmod +x main.sh

ENTRYPOINT ["./main.sh"]{% else %}ENTRYPOINT ["main"]{% endif %}
