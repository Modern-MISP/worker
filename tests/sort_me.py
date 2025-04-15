@pytest.mark.asyncio
async def test_correlation_plugin_job(init_api_config, user, correlation_test_event, correlation_exclusion):
    event: Event = correlation_test_event

    # setup
    correlation_test_plugin.register(correlation_plugin_factory)

    is_registered: bool = correlation_plugin_factory.is_plugin_registered(CorrelationTestPlugin.PLUGIN_INFO.NAME)
    assert is_registered
    plugin_info: CorrelationPluginInfo = correlation_plugin_factory.get_plugin_info("CorrelationTestPlugin")
    assert CorrelationTestPlugin.PLUGIN_INFO == plugin_info

    # test
    user: UserData = UserData(user_id=user.id)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="CorrelationTestPlugin", value=CORRELATION_VALUE
    )
    try:
        async_result = correlation_plugin_job.delay(user, data)
        result: CorrelateValueResponse = async_result.get()
    except Exception:
        print(async_result.traceback)
        print(async_result.traceback, file=sys.stderr)
        ic(async_result.traceback)
        assert False
    expected: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=True,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=[event.uuid],
    )
    assert expected == result

    data.value = correlation_exclusion.value
    result_excluded: CorrelateValueResponse = await correlation_plugin_job.run(user, data)
    expected_excluded: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=False,
        is_excluded_value=True,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=None,
    )
    assert expected_excluded == result_excluded

    data.value = "exception"
    try:
        await correlation_plugin_job.run(user, data)
    except Exception as e:
        assert e is not None

    data.value = "just_exception"
    try:
        await correlation_plugin_job.run(user, data)
    except Exception as e:
        assert e is not None

    data.value = "no_result"
    try:
        await correlation_plugin_job.run(user, data)
    except PluginExecutionException as e:
        assert "The result of the plugin was None." == str(e)

    data.value = "one"
    result_one: CorrelateValueResponse = await correlation_plugin_job.run(user, data)
    expected_one: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=False,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=None,
    )
    assert expected_one == result_one

    data.value = "instructor_fail"
    try:
        await correlation_plugin_job.run(user, data)
    except NotAValidPlugin as e:
        assert "Plugin 'CorrelationTestPlugin' has incorrect constructor: Test." == str(e)


@pytest.mark.asyncio
async def test_found_correlations(init_api_config, correlation_test_event, correlation_test_event_2):
    assert correlation_test_event.id != correlation_test_event_2.id

    test_data: CorrelateValueData = CorrelateValueData(value=CORRELATION_VALUE)
    result: CorrelateValueResponse = await correlate_value_job.run(user, test_data)

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is not None
    assert UUID(str(correlation_test_event.uuid)) in result.events
    assert UUID(str(correlation_test_event_2.uuid)) in result.events
