// WMK Geo Bridge — exemplo Node.js 18+ (sem dependências)
// Créditos: Walney Moreira Klein - walneyk@hotmail.com
const base = process.env.WMK_BRIDGE_URL || 'http://127.0.0.1:8766';
async function consultar(caminho) {
  const resposta = await fetch(base + caminho, { signal: AbortSignal.timeout(5000) });
  const dados = await resposta.json();
  console.log(caminho, 'HTTP', resposta.status, JSON.stringify(dados, null, 2));
  if (!resposta.ok) process.exitCode = 1;
}
(async () => {
  await consultar('/health');
  await consultar('/api/v1/capabilities');
  await consultar('/api/v1/vehicles');
})().catch(error => { console.error('Falha:', error.message); process.exitCode = 1; });
