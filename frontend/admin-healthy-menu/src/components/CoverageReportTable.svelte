<script>
    export let report = [];
</script>

<table class="min-w-full border">
    <thead>
        <tr>
            <th class="border px-4 py-2">Блюдо</th>
            <th class="border px-4 py-2">Орган</th>
            <th class="border px-4 py-2">Витамин</th>
            <th class="border px-4 py-2">Норма (мкг)</th>
            <th class="border px-4 py-2">В блюде (мкг)</th>
            <th class="border px-4 py-2">Покрытие (%)</th>
        </tr>
    </thead>
    <tbody>
        {#each report as item}
        <tr>
            <td class="border px-4 py-2">{item.dish_name}</td>
            <td class="border px-4 py-2">{item.organ_name}</td>
            <td class="border px-4 py-2">{item.vitamin_name}</td>
            <td class="border px-4 py-2">{item.daily_requirement_mcg}</td>
            <td class="border px-4 py-2">{item.vitamin_in_dish_mcg}</td>
            <td class="border px-4 py-2">{item.coverage_percentage.toFixed(2)}%</td>
        </tr>
        {/each}
    </tbody>
</table>
