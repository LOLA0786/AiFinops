from aifinops.cli import main

if __name__ == "__main__":
    main()

# extended CLI entrypoint
if __name__ == '__main__':
    try:
        import sys
        if len(sys.argv) > 1 and sys.argv[1] in ('attr','rightsize','zombies','predict','multicloud','llmguard','terraform_ai','slack','k8s','profit'):
            from aifinops.cli_ext import main as ext_main
            ext_main()
    except Exception:
        pass
