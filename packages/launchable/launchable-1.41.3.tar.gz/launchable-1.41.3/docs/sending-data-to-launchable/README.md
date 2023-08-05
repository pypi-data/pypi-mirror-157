# Sending data to Launchable

First, follow the steps in the [Getting started](../getting-started/) guide to sign up, set your API key, install the Launchable CLI, and verify your connection.

Then return to this page to complete the two steps for sending data:

1. Recording builds
2. Recording test results

The diagram below diagrams the high-level data flow:

![](../../.gitbook/assets/sending-data-diagram.png)

## Recording builds

Launchable Predictive Test Selection selects tests based on the Git changes in a [build.md](../concepts/build.md "mention") (among other data).

To send Git changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you record test results. See [Choosing a value for `<BUILD NAME>`](choosing-a-value-for-build-name.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository (or repositories) used to produce this build, such as `.` or `src`.

## Recording test results

Launchable also uses your test results from your [test-session.md](../concepts/test-session.md "mention")s.

After running tests, point the CLI to your test report files to collect test results for the build. Launchable uses the `<BUILD NAME>` value to connect the test results with the changes in the build:

```bash
launchable record tests --build <BUILD NAME> <TOOL NAME> <PATHS TO REPORT FILES>
```

The CLI natively integrates with the tools below. Click on the link to view instructions specific to your tool:

* [Android Debug Bridge (adb)](../resources/integrations/adb.md)
* [Ant](../resources/integrations/ant.md#recording-test-results)
* [Bazel](../resources/integrations/bazel.md#recording-test-results)
* [Behave](../resources/integrations/behave.md#recording-test-results)
* [CTest](../resources/integrations/ctest.md#recording-test-results)
* [cucumber](../resources/integrations/cucumber.md#recording-test-results)
* [Cypress](../resources/integrations/cypress.md#recording-test-results)
* [GoogleTest](../resources/integrations/googletest.md#recording-test-results)
* [Go Test](../resources/integrations/go-test.md#recording-test-results)
* [Gradle](../resources/integrations/gradle.md#recording-test-results)
* [Jest](../resources/integrations/jest.md#recording-test-results)
* [Maven](../resources/integrations/maven.md#recording-test-results)
* [minitest](../resources/integrations/minitest.md#recording-test-results)
* [nose](../resources/integrations/nose.md#recording-test-results)
* [NUnit](../resources/integrations/nunit.md#recording-test-results)
* [pytest](../resources/integrations/pytest.md#recording-test-results-pytest-plugin)
* [Robot](../resources/integrations/robot.md#recording-test-results)
* [RSpec](../resources/integrations/rspec.md#recording-test-results)

{% hint style="info" %}
If you're not using any of these, use the [generic 'file-based' runner integration](using-the-generic-file-based-runner-integration.md), the [`raw` profile for custom test runners](../resources/integrations/raw.md), or [request a plugin](mailto:support@launchableinc.com?subject=Request%20a%20plugin).
{% endhint %}

### Inspecting uploaded test results

You can use `launchable inspect tests` to inspect uploaded data. This is useful for verifying that you passed the correct report path(s) into `launchable record tests`. You can also see the values Launchable uses to identify individual tests.

The output from `launchable record tests` includes a tip to run `launchable inspect tests`:

```bash
$ launchable record tests --build 123 gradle reports/*.xml

< summary table >

Run `launchable inspect tests --test-session-id 209575` to view uploaded test results
```

Running that command will output a table containing a row for each test including:

* test identifier
* duration
* status (`PASSED`/`FAILED`/`SKIPPED`)
* uploaded timestamp

For brevity, this command does not output `stdout` or `stderr` (although they are stored).

## Next steps

Once you've started sending your builds and test results to Launchable, you can

1. See [trends.md](../features/insights/trends.md "mention") in your test sessions,
2. Find [flaky-tests.md](../features/insights/flaky-tests.md "mention"), and
3. Start [subsetting your test runs](../features/predictive-test-selection/subsetting-your-test-runs.md) with [predictive-test-selection](../features/predictive-test-selection/ "mention")
