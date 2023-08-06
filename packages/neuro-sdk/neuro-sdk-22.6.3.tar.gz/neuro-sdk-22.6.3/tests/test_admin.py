from decimal import Decimal
from typing import Callable

import pytest
from aiohttp import web
from aiohttp.web import HTTPNoContent
from aiohttp.web_exceptions import HTTPOk
from yarl import URL

from neuro_sdk import Client, NotSupportedError
from neuro_sdk._admin import (
    _CloudProvider,
    _ConfigCluster,
    _NodePool,
    _Storage,
    _StorageInstance,
)
from neuro_sdk._server_cfg import Preset

from tests import _TestServerFactory

_MakeClient = Callable[..., Client]


async def test_list_clusters(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handle_list_clusters(request: web.Request) -> web.StreamResponse:
        assert request.query["include"] == "cloud_provider_infra"
        data = [
            {"name": "default", "status": "deployed"},
            {"name": "other", "status": "deployed"},
        ]
        return web.json_response(data)

    app = web.Application()
    app.router.add_get("/api/v1/clusters", handle_list_clusters)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1")) as client:
        clusters = await client._admin.list_config_clusters()
        assert clusters == {
            "default": _ConfigCluster(name="default", status="deployed"),
            "other": _ConfigCluster(name="other", status="deployed"),
        }


async def test_list_clusters_with_cloud_provider(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def handle_list_clusters(request: web.Request) -> web.StreamResponse:
        assert request.query["include"] == "cloud_provider_infra"
        data = [
            {
                "name": "default",
                "status": "deployed",
                "cloud_provider": {
                    "type": "gcp",
                    "region": "us-central1",
                    "zone": "us-central1-a",
                    "node_pools": [
                        {
                            "machine_type": "n1-highmem-8",
                            "min_size": 1,
                            "max_size": 2,
                            "idle_size": 1,
                            "available_cpu": 7,
                            "available_memory_mb": 46080,
                            "disk_type": "ssd",
                            "disk_size_gb": 150,
                            "gpu": 1,
                            "gpu_model": "nvidia-tesla-k80",
                            "is_preemptible": True,
                        },
                        {
                            "machine_type": "n1-highmem-8",
                            "min_size": 1,
                            "max_size": 2,
                            "available_cpu": 7,
                            "available_memory_mb": 46080,
                            "disk_size_gb": 150,
                        },
                    ],
                    "storage": {
                        "description": "Filestore",
                        "instances": [
                            {"size_mb": 1024},
                            {"name": "org", "size_mb": 1024},
                        ],
                    },
                },
            },
            {
                "name": "on-prem",
                "status": "deployed",
                "cloud_provider": {
                    "type": "on_prem",
                    "node_pools": [
                        {
                            "min_size": 2,
                            "max_size": 2,
                            "machine_type": "n1-highmem-8",
                            "available_cpu": 7,
                            "available_memory_mb": 46080,
                            "disk_size_gb": 150,
                        },
                    ],
                    "storage": {
                        "description": "NFS",
                        "instances": [{"size_mb": 1024}],
                    },
                },
            },
            {
                "name": "other1",
                "status": "deployed",
                "cloud_provider": {
                    "type": "gcp",
                    "region": "us-central1",
                    "zones": ["us-central1-a", "us-central1-c"],
                },
            },
            {
                "name": "other2",
                "status": "deployed",
                "cloud_provider": {"type": "aws", "region": "us-central1"},
            },
        ]
        return web.json_response(data)

    app = web.Application()
    app.router.add_get("/api/v1/clusters", handle_list_clusters)

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1")) as client:
        clusters = await client._admin.list_config_clusters()
        assert clusters == {
            "default": _ConfigCluster(
                name="default",
                status="deployed",
                cloud_provider=_CloudProvider(
                    type="gcp",
                    region="us-central1",
                    zones=["us-central1-a"],
                    node_pools=[
                        _NodePool(
                            min_size=1,
                            max_size=2,
                            idle_size=1,
                            machine_type="n1-highmem-8",
                            available_cpu=7.0,
                            available_memory_mb=46080,
                            disk_type="ssd",
                            disk_size_gb=150,
                            gpu=1,
                            gpu_model="nvidia-tesla-k80",
                            is_preemptible=True,
                        ),
                        _NodePool(
                            min_size=1,
                            max_size=2,
                            machine_type="n1-highmem-8",
                            available_cpu=7.0,
                            available_memory_mb=46080,
                            disk_size_gb=150,
                        ),
                    ],
                    storage=_Storage(
                        description="Filestore",
                        instances=[
                            _StorageInstance(size_mb=1024),
                            _StorageInstance(name="org", size_mb=1024),
                        ],
                    ),
                ),
            ),
            "on-prem": _ConfigCluster(
                name="on-prem",
                status="deployed",
                cloud_provider=_CloudProvider(
                    type="on_prem",
                    region=None,
                    zones=[],
                    node_pools=[
                        _NodePool(
                            min_size=2,
                            max_size=2,
                            machine_type="n1-highmem-8",
                            disk_size_gb=150,
                            available_cpu=7.0,
                            available_memory_mb=46080,
                        ),
                    ],
                    storage=_Storage(
                        description="NFS",
                        instances=[_StorageInstance(size_mb=1024)],
                    ),
                ),
            ),
            "other1": _ConfigCluster(
                name="other1",
                status="deployed",
                cloud_provider=_CloudProvider(
                    type="gcp",
                    region="us-central1",
                    zones=["us-central1-a", "us-central1-c"],
                    node_pools=[],
                    storage=None,
                ),
            ),
            "other2": _ConfigCluster(
                name="other2",
                status="deployed",
                cloud_provider=_CloudProvider(
                    type="aws",
                    region="us-central1",
                    zones=[],
                    node_pools=[],
                    storage=None,
                ),
            ),
        }


async def test_add_cluster(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    create_cluster_json = None
    put_cloud_json = None
    # GCP cloud provider example from
    # https://github.com/neuro-inc/platform-config#configuring-cloud-provider
    JSON = {
        "type": "gcp",
        "location_type": "zonal",
        "region": "us-central1",
        "zone": "us-central1-a",
        "project": "project",
        "tpu_enabled": True,
        "credentials": {
            "type": "service_account",
            "project_id": "project_id",
            "private_key_id": "private_key_id",
            "private_key": "private_key",
            "client_email": "service.account@gmail.com",
            "client_id": "client_id",
            "auth_uri": "https://auth_uri",
            "token_uri": "https://token_uri",
            "auth_provider_x509_cert_url": "https://auth_provider_x509_cert_url",
            "client_x509_cert_url": "https://client_x509_cert_url",
        },
        "node_pools": [
            {
                "id": "n1_highmem_8",  # id of the GCP node pool template
                "min_size": 0,
                "max_size": 5,
            },
            {"id": "n1_highmem_32_4x_nvidia_tesla_k80", "min_size": 0, "max_size": 5},
            {
                "id": "n1_highmem_32_4x_nvidia_tesla_k80",
                "min_size": 0,
                "max_size": 5,
                "is_preemptible": True,
            },
        ],
        "storage": {
            "id": "premium",  # id of the GCP storage template
            "instances": [{"size_mb": 1024}],
        },
    }

    async def handle_create_cluster(request: web.Request) -> web.StreamResponse:
        nonlocal create_cluster_json
        create_cluster_json = await request.json()
        return web.json_response(create_cluster_json, status=201)

    async def handle_put_cloud_provider(request: web.Request) -> web.StreamResponse:
        nonlocal put_cloud_json
        assert request.query["start_deployment"] == "true"
        put_cloud_json = await request.json()
        return web.Response(status=201)

    app = web.Application()
    app.router.add_post("/apis/admin/v1/clusters", handle_create_cluster)
    app.router.add_put(
        "/api/v1/clusters/default/cloud_provider", handle_put_cloud_provider
    )

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1")) as client:
        await client._admin.create_cluster("default")
        await client._admin.setup_cluster_cloud_provider("default", JSON)

    assert create_cluster_json == {
        "name": "default",
        "default_quota": {},
        "default_role": "user",
        "maintenance": False,
    }
    assert put_cloud_json == JSON


async def test_not_supported_admin_api(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    app = web.Application()

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1"), admin_url=URL()) as client:
        with pytest.raises(
            NotSupportedError, match="admin API is not supported by server"
        ):
            await client._admin.get_cluster_user("default", "test")


async def test_get_cloud_provider_options(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    sample_response = {"foo": "bar"}

    async def handle_cloud_providers(
        request: web.Request,
    ) -> web.Response:
        return web.json_response(sample_response, status=HTTPOk.status_code)

    app = web.Application()
    app.router.add_get(
        "/api/v1/cloud_providers/aws",
        handle_cloud_providers,
    )

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1")) as client:
        result = await client._admin.get_cloud_provider_options("aws")
        assert result == sample_response


async def test_update_cluster_resource_presets(
    aiohttp_server: _TestServerFactory, make_client: _MakeClient
) -> None:
    async def update_cluster_resource_presets(
        request: web.Request,
    ) -> web.StreamResponse:
        assert request.match_info["cluster_name"] == "my_cluster"
        assert sorted(await request.json(), key=lambda x: x["name"]) == [
            {
                "name": "cpu-micro",
                "credits_per_hour": "10",
                "cpu": 0.1,
                "memory_mb": 100,
                "scheduler_enabled": False,
                "preemptible_node": False,
            },
            {
                "name": "cpu-micro-p",
                "credits_per_hour": "10",
                "cpu": 0.1,
                "memory_mb": 100,
                "scheduler_enabled": True,
                "preemptible_node": True,
            },
            {
                "name": "gpu-micro",
                "credits_per_hour": "10",
                "cpu": 0.2,
                "memory_mb": 200,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-k80",
                "scheduler_enabled": False,
                "preemptible_node": False,
            },
            {
                "name": "tpu-micro",
                "credits_per_hour": "10",
                "cpu": 0.3,
                "memory_mb": 300,
                "tpu": {"type": "v2-8", "software_version": "1.14"},
                "scheduler_enabled": False,
                "preemptible_node": False,
            },
        ]
        return web.Response(status=HTTPNoContent.status_code)

    app = web.Application()
    app.router.add_put(
        "/api/v1/clusters/{cluster_name}/orchestrator/resource_presets",
        update_cluster_resource_presets,
    )

    srv = await aiohttp_server(app)

    async with make_client(srv.make_url("/api/v1")) as client:
        await client._admin.update_cluster_resource_presets(
            "my_cluster",
            {
                "cpu-micro": Preset(
                    credits_per_hour=Decimal("10"), cpu=0.1, memory_mb=100
                ),
                "cpu-micro-p": Preset(
                    credits_per_hour=Decimal("10"),
                    cpu=0.1,
                    memory_mb=100,
                    scheduler_enabled=True,
                    preemptible_node=True,
                ),
                "gpu-micro": Preset(
                    credits_per_hour=Decimal("10"),
                    cpu=0.2,
                    memory_mb=200,
                    gpu=1,
                    gpu_model="nvidia-tesla-k80",
                ),
                "tpu-micro": Preset(
                    credits_per_hour=Decimal("10"),
                    cpu=0.3,
                    memory_mb=300,
                    tpu_type="v2-8",
                    tpu_software_version="1.14",
                ),
            },
        )
