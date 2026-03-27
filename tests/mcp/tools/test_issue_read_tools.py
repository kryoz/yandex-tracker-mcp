from unittest.mock import AsyncMock

from mcp.client.session import ClientSession

from mcp_tracker.tracker.proto.types.issues import (
    ChecklistItem,
    Issue,
    IssueAttachment,
    IssueComment,
    IssueLink,
    IssueTransition,
    Worklog,
)
from tests.mcp.conftest import get_tool_result_content


class TestIssueGetUrl:
    async def test_returns_tracker_url(
        self,
        client_session: ClientSession,
    ) -> None:
        result = await client_session.call_tool(
            "issue_get_url", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        content = get_tool_result_content(result)
        assert content == "https://tracker.yandex.ru/TEST-123"


class TestIssueGet:
    async def test_returns_issue(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issue: Issue,
    ) -> None:
        mock_issues_protocol.issue_get.return_value = sample_issue

        result = await client_session.call_tool("issue_get", {"issue_id": "TEST-123"})

        assert not result.isError
        mock_issues_protocol.issue_get.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, dict)
        assert content["key"] == sample_issue.key
        assert content["summary"] == sample_issue.summary

    async def test_with_description_excluded(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issue: Issue,
    ) -> None:
        mock_issues_protocol.issue_get.return_value = sample_issue

        result = await client_session.call_tool(
            "issue_get", {"issue_id": "TEST-123", "include_description": False}
        )

        assert not result.isError
        mock_issues_protocol.issue_get.assert_called_once()
        content = get_tool_result_content(result)
        assert content["key"] == sample_issue.key
        # Description should be None when excluded
        assert content.get("description") is None

    async def test_restricted_queue_raises_error(
        self,
        client_session_with_limits: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        result = await client_session_with_limits.call_tool(
            "issue_get", {"issue_id": "RESTRICTED-123"}
        )

        assert result.isError
        mock_issues_protocol.issue_get.assert_not_called()


class TestIssueGetComments:
    async def test_returns_comments(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_comments: list[IssueComment],
    ) -> None:
        mock_issues_protocol.issue_get_comments.return_value = sample_comments

        result = await client_session.call_tool(
            "issue_get_comments", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issue_get_comments.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_comments)
        assert content[0]["text"] == sample_comments[0].text

    async def test_restricted_queue_raises_error(
        self,
        client_session_with_limits: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        result = await client_session_with_limits.call_tool(
            "issue_get_comments", {"issue_id": "RESTRICTED-123"}
        )

        assert result.isError
        mock_issues_protocol.issue_get_comments.assert_not_called()


class TestIssueGetLinks:
    async def test_returns_links(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_links: list[IssueLink],
    ) -> None:
        mock_issues_protocol.issues_get_links.return_value = sample_links

        result = await client_session.call_tool(
            "issue_get_links", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issues_get_links.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_links)
        assert content[0]["direction"] == sample_links[0].direction


class TestIssueGetLinkKeys:
    async def test_returns_link_keys(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_links: list[IssueLink],
    ) -> None:
        mock_issues_protocol.issues_get_links.return_value = sample_links

        result = await client_session.call_tool(
            "issue_get_link_keys", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issues_get_links.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert content == ["TEST-456"]

    async def test_returns_empty_list_when_no_links(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        mock_issues_protocol.issues_get_links.return_value = []

        result = await client_session.call_tool(
            "issue_get_link_keys", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        content = get_tool_result_content(result)
        assert content == []

    async def test_excludes_links_without_key(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_link: IssueLink,
    ) -> None:
        from mcp_tracker.tracker.proto.types.refs import IssueReference

        links_with_none_key = [
            sample_link,
            IssueLink.model_construct(
                id=2,
                object=None,
            ),
        ]
        mock_issues_protocol.issues_get_links.return_value = links_with_none_key

        result = await client_session.call_tool(
            "issue_get_link_keys", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        content = get_tool_result_content(result)
        assert content == ["TEST-456"]

    async def test_restricted_queue_raises_error(
        self,
        client_session_with_limits: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        result = await client_session_with_limits.call_tool(
            "issue_get_link_keys", {"issue_id": "RESTRICTED-123"}
        )

        assert result.isError
        mock_issues_protocol.issues_get_links.assert_not_called()


class TestIssuesFind:
    async def test_finds_issues(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool("issues_find", {"query": "Queue: TEST"})

        assert not result.isError
        mock_issues_protocol.issues_find.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_issues)
        assert content[0]["key"] == sample_issues[0].key

    async def test_with_pagination(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool(
            "issues_find", {"query": "Queue: TEST", "page": 2, "per_page": 50}
        )

        assert not result.isError
        call_kwargs = mock_issues_protocol.issues_find.call_args.kwargs
        assert call_kwargs["page"] == 2
        assert call_kwargs["per_page"] == 50
        content = get_tool_result_content(result)
        assert len(content) == len(sample_issues)

    async def test_excludes_description_by_default(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool("issues_find", {"query": "Queue: TEST"})

        assert not result.isError
        mock_issues_protocol.issues_find.assert_called_once()
        content = get_tool_result_content(result)
        # By default, description is excluded (set to None)
        for issue in content:
            assert issue.get("description") is None


class TestIssuesFindLight:
    async def test_finds_issues_with_light_fields(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool(
            "issues_find_light", {"query": "Queue: TEST"}
        )

        assert not result.isError
        mock_issues_protocol.issues_find.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_issues)
        # Key и summary должны быть заполнены
        assert content[0]["key"] == sample_issues[0].key
        assert content[0]["summary"] == sample_issues[0].summary

    async def test_only_key_summary_description_fields(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        """Проверяет, что только ключевые поля возвращаются."""
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool(
            "issues_find_light", {"query": "Queue: TEST"}
        )

        assert not result.isError
        content = get_tool_result_content(result)
        # Проверяем, что другие поля установлены в None
        for issue in content:
            # Эти поля должны быть заполнены
            assert "key" in issue
            assert "summary" in issue
            # description может быть None или заполнен
            # Остальные поля должны быть None или отсутствовать
            for field in ["type", "priority", "assignee", "status"]:
                assert issue.get(field) is None

    async def test_with_pagination(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_issues: list[Issue],
    ) -> None:
        mock_issues_protocol.issues_find.return_value = sample_issues

        result = await client_session.call_tool(
            "issues_find_light",
            {"query": "Queue: TEST", "page": 2, "per_page": 50},
        )

        assert not result.isError
        call_kwargs = mock_issues_protocol.issues_find.call_args.kwargs
        assert call_kwargs["page"] == 2
        assert call_kwargs["per_page"] == 50
        content = get_tool_result_content(result)
        assert len(content) == len(sample_issues)


class TestIssuesCount:
    async def test_returns_count(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        mock_issues_protocol.issues_count.return_value = 42

        result = await client_session.call_tool(
            "issues_count", {"query": "Queue: TEST"}
        )

        assert not result.isError
        mock_issues_protocol.issues_count.assert_called_once()
        content = get_tool_result_content(result)
        assert content == 42


class TestIssueGetWorklogs:
    async def test_returns_worklogs_for_multiple_issues(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_worklogs: list[Worklog],
    ) -> None:
        mock_issues_protocol.issue_get_worklogs.return_value = sample_worklogs

        result = await client_session.call_tool(
            "issue_get_worklogs", {"issue_ids": ["TEST-123", "TEST-124"]}
        )

        assert not result.isError
        # Should be called once per issue
        assert mock_issues_protocol.issue_get_worklogs.call_count == 2
        content = get_tool_result_content(result)
        assert isinstance(content, dict)
        assert "TEST-123" in content
        assert "TEST-124" in content
        assert len(content["TEST-123"]) == len(sample_worklogs)

    async def test_restricted_queue_raises_error(
        self,
        client_session_with_limits: ClientSession,
        mock_issues_protocol: AsyncMock,
    ) -> None:
        result = await client_session_with_limits.call_tool(
            "issue_get_worklogs", {"issue_ids": ["RESTRICTED-123"]}
        )

        assert result.isError
        mock_issues_protocol.issue_get_worklogs.assert_not_called()


class TestIssueGetAttachments:
    async def test_returns_attachments(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_attachments: list[IssueAttachment],
    ) -> None:
        mock_issues_protocol.issue_get_attachments.return_value = sample_attachments

        result = await client_session.call_tool(
            "issue_get_attachments", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issue_get_attachments.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_attachments)
        assert content[0]["name"] == sample_attachments[0].name


class TestIssueGetChecklist:
    async def test_returns_checklist(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_checklist: list[ChecklistItem],
    ) -> None:
        mock_issues_protocol.issue_get_checklist.return_value = sample_checklist

        result = await client_session.call_tool(
            "issue_get_checklist", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issue_get_checklist.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_checklist)
        assert content[0]["text"] == sample_checklist[0].text


class TestIssueGetTransitions:
    async def test_returns_transitions(
        self,
        client_session: ClientSession,
        mock_issues_protocol: AsyncMock,
        sample_transitions: list[IssueTransition],
    ) -> None:
        mock_issues_protocol.issue_get_transitions.return_value = sample_transitions

        result = await client_session.call_tool(
            "issue_get_transitions", {"issue_id": "TEST-123"}
        )

        assert not result.isError
        mock_issues_protocol.issue_get_transitions.assert_called_once()
        content = get_tool_result_content(result)
        assert isinstance(content, list)
        assert len(content) == len(sample_transitions)
        assert content[0]["id"] == sample_transitions[0].id
        assert content[0]["display"] == sample_transitions[0].display
