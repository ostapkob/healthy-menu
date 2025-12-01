<script>
    import { onMount } from 'svelte';
    import CoverageReportTable from '../../components/CoverageReportTable.svelte';

    let report = [];

    onMount(async () => {
        const response = await fetch('http://localhost:8001/coverage-report/');
        report = await response.json();
    });
</script>

<h2 class="text-xl font-bold mb-4">Покрытие витаминов</h2>

{#if report.length > 0}
    <CoverageReportTable {report} />
{:else}
    <p>Нет данных</p>
{/if}
