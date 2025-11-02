#!/usr/bin/env python3
"""Benchmark chunking performance on 100 GitHub repos."""
import time
import subprocess
from datetime import datetime

# Small to medium-sized repos for testing chunking (exactly 100 repos)
REPOS = [
    # Python projects
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
    
    # JavaScript/Node.js projects
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
    
    # React projects
    "https://github.com/reduxjs/redux",
    "https://github.com/pmndrs/zustand",
    "https://github.com/react-hook-form/react-hook-form",
    "https://github.com/formik/formik",
    
    # Go projects
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
    
    # Rust projects
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
    
    # Java projects
    "https://github.com/google/gson",
    "https://github.com/square/okhttp",
    "https://github.com/junit-team/junit5",
    "https://github.com/mockito/mockito",
    "https://github.com/apache/commons-lang",
    "https://github.com/apache/commons-io",
    "https://github.com/FasterXML/jackson-core",
    "https://github.com/eclipse-vertx/vert.x",
    
    # C# projects
    "https://github.com/AutoMapper/AutoMapper",
    "https://github.com/serilog/serilog",
    "https://github.com/FluentValidation/FluentValidation",
    "https://github.com/JamesNK/Newtonsoft.Json",
    "https://github.com/nunit/nunit",
    "https://github.com/xunit/xunit",
    
    # PHP projects
    "https://github.com/guzzle/guzzle",
    "https://github.com/monolog/monolog",
    "https://github.com/phpunit/phpunit",
    "https://github.com/symfony/symfony",
    "https://github.com/doctrine/orm",
    "https://github.com/fzaninotto/Faker",
    
    # Ruby projects
    "https://github.com/rspec/rspec",
    "https://github.com/rubocop/rubocop",
    "https://github.com/puma/puma",
    "https://github.com/sidekiq/sidekiq",
    "https://github.com/thoughtbot/factory_bot",
    "https://github.com/faker-ruby/faker",
    
    # TypeScript projects
    "https://github.com/microsoft/TypeScript",
    "https://github.com/typeorm/typeorm",
    "https://github.com/nestjs/nest",
    
    # Utility/CLI tools
    "https://github.com/BurntSushi/ripgrep",
    "https://github.com/sharkdp/fd",
    "https://github.com/ogham/exa",
    "https://github.com/dandavison/delta",
    
    # Testing frameworks
    "https://github.com/mochajs/mocha",
    "https://github.com/jasmine/jasmine",
    "https://github.com/avajs/ava",
    "https://github.com/tape-testing/tape",
    
    # Database libraries
    "https://github.com/redis/node-redis",
    "https://github.com/brianc/node-postgres",
    "https://github.com/mysqljs/mysql",
    "https://github.com/mongodb/node-mongodb-native",
    "https://github.com/sequelize/sequelize",
    
    # Web frameworks
    "https://github.com/pallets/flask",
    "https://github.com/bottlepy/bottle",
    "https://github.com/koajs/koa",
    "https://github.com/fastify/fastify",
    
    # Build tools & CSS
    "https://github.com/gulpjs/gulp",
    "https://github.com/sass/sass",
    "https://github.com/postcss/postcss",
    "https://github.com/twbs/bootstrap",
    
    # More utilities
    "https://github.com/tj/commander.js",
    "https://github.com/enquirer/enquirer",
    "https://github.com/SBoudrias/Inquirer.js",
    "https://github.com/sindresorhus/execa",
]


def run_chunk_command(repo_url, index, total):
    """Run chunking command for a single repo."""
    print(f"\n{'='*80}")
    print(f"[{index}/{total}] Processing: {repo_url}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["python", "-m", "src.cli", "chunk", "--save", "--repo-url", repo_url, "--save-ast"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per repo
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS in {elapsed:.2f}s")
            return {
                'repo': repo_url,
                'status': 'success',
                'time': elapsed,
                'output': result.stdout
            }
        else:
            print(f"❌ FAILED in {elapsed:.2f}s")
            print(f"Error: {result.stderr}")
            return {
                'repo': repo_url,
                'status': 'failed',
                'time': elapsed,
                'error': result.stderr
            }
    
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"⏱️  TIMEOUT after {elapsed:.2f}s")
        return {
            'repo': repo_url,
            'status': 'timeout',
            'time': elapsed
        }
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"💥 ERROR: {e}")
        return {
            'repo': repo_url,
            'status': 'error',
            'time': elapsed,
            'error': str(e)
        }


def main():
    """Run benchmark on all repos."""
    print("\n" + "="*80)
    print("🚀 BENCHMARK: Chunking 100 GitHub Repositories")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total repos: {len(REPOS)}")
    print("="*80)
    
    overall_start = time.time()
    results = []
    
    # Process each repo
    for i, repo_url in enumerate(REPOS, 1):
        result = run_chunk_command(repo_url, i, len(REPOS))
        results.append(result)
        
        # Progress summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        timeout_count = sum(1 for r in results if r['status'] == 'timeout')
        
        print(f"\n📊 Progress: {i}/{len(REPOS)} | ✅ {success_count} | ❌ {failed_count} | ⏱️  {timeout_count}")
    
    overall_elapsed = time.time() - overall_start
    
    # Final statistics
    print("\n" + "="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    
    success_results = [r for r in results if r['status'] == 'success']
    failed_results = [r for r in results if r['status'] == 'failed']
    timeout_results = [r for r in results if r['status'] == 'timeout']
    
    print(f"\n✅ Successful: {len(success_results)}/{len(REPOS)}")
    print(f"❌ Failed: {len(failed_results)}/{len(REPOS)}")
    print(f"⏱️  Timeout: {len(timeout_results)}/{len(REPOS)}")
    
    if success_results:
        times = [r['time'] for r in success_results]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n⏱️  Timing Statistics (successful repos):")
        print(f"   Average: {avg_time:.2f}s per repo")
        print(f"   Fastest: {min_time:.2f}s")
        print(f"   Slowest: {max_time:.2f}s")
        print(f"   Total:   {sum(times):.2f}s")
    
    print(f"\n🕐 Overall Time: {overall_elapsed:.2f}s ({overall_elapsed/60:.2f} minutes)")
    print(f"   Average per repo: {overall_elapsed/len(REPOS):.2f}s")
    
    # Throughput
    repos_per_minute = (len(REPOS) / overall_elapsed) * 60
    print(f"\n🚀 Throughput: {repos_per_minute:.2f} repos/minute")
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"benchmark_results_{timestamp}.txt"
    
    with open(output_file, 'w') as f:
        f.write(f"Benchmark Results - {datetime.now()}\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total repos: {len(REPOS)}\n")
        f.write(f"Successful: {len(success_results)}\n")
        f.write(f"Failed: {len(failed_results)}\n")
        f.write(f"Timeout: {len(timeout_results)}\n")
        f.write(f"Overall time: {overall_elapsed:.2f}s\n")
        f.write(f"Throughput: {repos_per_minute:.2f} repos/minute\n\n")
        
        f.write("Detailed Results:\n")
        f.write("-"*80 + "\n")
        for r in results:
            f.write(f"\n{r['repo']}\n")
            f.write(f"  Status: {r['status']}\n")
            f.write(f"  Time: {r['time']:.2f}s\n")
            if 'error' in r:
                f.write(f"  Error: {r['error']}\n")
    
    print(f"\n💾 Results saved to: {output_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
