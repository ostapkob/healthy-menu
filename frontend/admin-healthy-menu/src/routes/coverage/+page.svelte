<script>
    import { onMount } from 'svelte';
    import CoverageReportTable from '../../components/CoverageReportTable.svelte';
    // const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для разработки
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'; // Значение по умолчанию для dev


    let report = [];

    onMount(async () => {
        const response = await fetch(`${API_BASE_URL}/coverage-report/`);
        report = await response.json();
    });
</script>

<h2 class="text-xl font-bold mb-4">Покрытие витаминов</h2>

{#if report.length > 0}
    <CoverageReportTable {report} />
{:else}
    <p>Нет данных</p>
{/if}
