#!/usr/bin/env python3
"""Optimized benchmark for chunking 100 GitHub repos with resource management."""
import os
import time
import subprocess
from datetime import datetime

# Same repo list as original
REPOS = [
    "https://github.com/psf/requests",
    "https://github.com/pallets/click",
    "https://github.com/pytest-dev/pytest",
    "https://github.com/python-poetry/poetry",
    "https://github.com/tiangolo/fastapi",
    "https://github.com/encode/httpx",
    "https://github.com/pydantic/pydantic",
    "https://github.com/celery/celery",
    "https://github.com/sqlalchemy/sqlalchemy",
    "https://github.com/marshmallow-code/marshmallow",
    "https://github.com/expressjs/express",
    "https://github.com/lodash/lodash",
    "https://github.com/axios/axios",
    "https://github.com/chalk/chalk",
    "https://github.com/sindresorhus/got",
    "https://github.com/yargs/yargs",
    "https://github.com/debug-js/debug",
    "https://github.com/moment/moment",
    "https://github.com/date-fns/date-fns",
    "https://github.com/ramda/ramda",
    "https://github.com/reduxjs/redux",
    "https://github.com/pmndrs/zustand",
    "https://github.com/react-hook-form/react-hook-form",
    "https://github.com/formik/formik",
    "https://github.com/gin-gonic/gin",
    "https://github.com/gorilla/mux",
    "https://github.com/spf13/cobra",
    "https://github.com/sirupsen/logrus",
    "https://github.com/stretchr/testify",
    "https://github.com/go-chi/chi",
    "https://github.com/labstack/echo",
    "https://github.com/gofiber/fiber",
    "https://github.com/urfave/cli",
    "https://github.com/spf13/viper",
    "https://github.com/clap-rs/clap",
    "https://github.com/serde-rs/serde",
    "https://github.com/tokio-rs/tokio",
    "https://github.com/actix/actix-web",
    "https://github.com/hyperium/hyper",
    "https://github.com/rayon-rs/rayon",
    "https://github.com/diesel-rs/diesel",
    "https://github.com/rust-random/rand",
    "https://github.com/chronotope/chrono",
    "https://github.com/uuid-rs/uuid",
    "https://github.com/google/gson",
    "https://github.com/square/okhttp",
    "https://github.com/junit-team/junit5",
    "https://github.com/mockito/mockito",
    "https://github.com/apache/commons-lang",
    "https://github.com/apache/commons-io",
    "https://github.com/FasterXML/jackson-core",
    "https://github.com/eclipse-vertx/vert.x",
    "https://github.com/AutoMapper/AutoMapper",
    "https://github.com/serilog/serilog",
    "https://github.com/FluentValidation/FluentValidation",
    "https://github.com/JamesNK/Newtonsoft.Json",
    "https://github.com/nunit/nunit",
    "https://github.com/xunit/xunit",
    "https://github.com/guzzle/guzzle",
    "https://github.com/monolog/monolog",
    "https://github.com/phpunit/phpunit",
    "https://github.com/symfony/symfony",
    "https://github.com/doctrine/orm",
    "https://github.com/fzaninotto/Faker",
    "https://github.com/rspec/rspec",
    "https://github.com/rubocop/rubocop",
    "https://github.com/puma/puma",
    "https://github.com/sidekiq/sidekiq",
    "https://github.com/thoughtbot/factory_bot",
    "https://github.com/faker-ruby/faker",
    "https://github.com/microsoft/TypeScript",
    "https://github.com/typeorm/typeorm",
    "https://github.com/nestjs/nest",
    "https://github.com/BurntSushi/ripgrep",
    "https://github.com/sharkdp/fd",
    "https://github.com/ogham/exa",
    "https://github.com/dandavison/delta",
    "https://github.com/mochajs/mocha",
    "https://github.com/jasmine/jasmine",
    "https://github.com/avajs/ava",
    "https://github.com/tape-testing/tape",
    "https://github.com/redis/node-redis",
    "https://github.com/brianc/node-postgres",
    "https://github.com/mysqljs/mysql",
    "https://github.com/mongodb/node-mongodb-native",
    "https://github.com/sequelize/sequelize",
    "https://github.com/pallets/flask",
    "https://github.com/bottlepy/bottle",
    "https://github.com/koajs/koa",
    "https://github.com/fastify/fastify",
    "https://github.com/gulpjs/gulp",
    "https://github.com/sass/sass",
    "https://github.com/postcss/postcss",
    "https://github.com/twbs/bootstrap",
    "https://github.com/tj/commander.js",
    "https://github.com/enquirer/enquirer",
    "https://github.com/SBoudrias/Inquirer.js",
    "https://github.com/sindresorhus/execa",
]


def run_chunk_command(repo_url, index, total):
    """Run chunking with limited workers to prevent resource exhaustion."""
    print(f"\n[{index}/{total}] {repo_url}")
    
    start_time = time.time()
    
    try:
        # Key fix: Use environment variable to limit workers
        env = {"CONTEXTINATOR_MAX_WORKERS": "2"}  # Limit to 2 workers max
        
        result = subprocess.run(
            ["python", "-m", "src.cli", "chunk", "--save", "--repo-url", repo_url],
            capture_output=True,
            text=True,
            timeout=180,  # Reduced timeout
            env={**dict(os.environ), **env}  # Merge with existing env
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {elapsed:.1f}s")
            return {'repo': repo_url, 'status': 'success', 'time': elapsed}
        else:
            print(f"❌ {elapsed:.1f}s - {result.stderr[:100]}")
            return {'repo': repo_url, 'status': 'failed', 'time': elapsed}
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT")
        return {'repo': repo_url, 'status': 'timeout', 'time': 180}
    
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return {'repo': repo_url, 'status': 'error', 'time': 0}


def main():
    import os
    
    print(f"🚀 Benchmarking {len(REPOS)} repos with resource limits")
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    results = []
    
    for i, repo in enumerate(REPOS, 1):
        result = run_chunk_command(repo, i, len(REPOS))
        results.append(result)
        
        # Brief pause to let system recover
        if i % 10 == 0:
            print(f"\n--- Processed {i}/{len(REPOS)} repos ---")
            time.sleep(2)
    
    elapsed = time.time() - start_time
    success = sum(1 for r in results if r['status'] == 'success')
    
    print(f"\n📊 Results: {success}/{len(REPOS)} successful in {elapsed/60:.1f}m")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"benchmark_{timestamp}.txt", 'w') as f:
        f.write(f"Benchmark Results - {datetime.now()}\n")
        f.write(f"Success: {success}/{len(REPOS)}\n")
        f.write(f"Time: {elapsed:.1f}s\n\n")
        for r in results:
            f.write(f"{r['status']:<8} {r['time']:>6.1f}s {r['repo']}\n")


if __name__ == "__main__":
    main()
