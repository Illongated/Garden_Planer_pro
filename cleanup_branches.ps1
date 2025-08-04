# Script pour nettoyer toutes les branches sauf main
Write-Host "🧹 Nettoyage des branches..." -ForegroundColor Green

# Supprimer les branches distantes
$branches = @(
    "add-update-scripts",
    "feat/agrotique-frontend-rebuild",
    "feat/complete-auth-system", 
    "feat/database-layer-implementation",
    "feat/full-fastapi-implementation",
    "feat/garden-editor-v1",
    "feat/garden-planner",
    "feat/garden-planner-full-stack",
    "feat/interactive-garden-planner",
    "feat/major-optimization-and-cicd-fixes",
    "feat/postgres-re-architecture",
    "feat/re-architect-garden-planner",
    "feature/garden-planner-interactive",
    "feature/garden-planner-pro",
    "feature/intelligent-layout-engine",
    "feature/setup-scripts",
    "fix-frontend-js-errors",
    "fix/blank-page-and-rename-scripts"
)

foreach ($branch in $branches) {
    Write-Host "Suppression de la branche: $branch" -ForegroundColor Yellow
    git push origin --delete $branch 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $branch supprimée" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $branch non supprimée (peut-être déjà supprimée)" -ForegroundColor Yellow
    }
}

# Supprimer les références locales
Write-Host "`n🧹 Nettoyage des références locales..." -ForegroundColor Green
git remote prune origin

Write-Host "`n✅ Nettoyage terminé !" -ForegroundColor Green
Write-Host "Il ne reste que la branche main avec la version optimisée." -ForegroundColor Cyan 