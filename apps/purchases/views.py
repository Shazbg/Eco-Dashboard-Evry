from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PurchaseData
from .forms import PurchaseDataForm


@login_required
def purchase_form(request):
    """Vue du formulaire de saisie d'achat."""
    if request.method == 'POST':
        form = PurchaseDataForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.save()
            
            messages.success(
                request,
                f'✅ Achat enregistré ! Impact carbone : {purchase.total_co2_kg:.2f} kg CO₂e'
            )
            return redirect('purchase_list')
    else:
        form = PurchaseDataForm(initial={'year': 2026})
    
    # Récupérer les facteurs d'émission pour affichage dynamique
    emission_factors = PurchaseData.EMISSION_FACTORS
    
    return render(request, 'purchases/purchase_form.html', {
        'form': form,
        'emission_factors': emission_factors
    })


@login_required
def purchase_list(request):
    """Vue listant toutes les données d'achats de l'utilisateur."""
    purchases = PurchaseData.objects.filter(user=request.user)
    
    # Statistiques
    total_co2 = sum(p.total_co2_kg for p in purchases)
    total_amount = sum(p.amount_euros for p in purchases)
    
    return render(request, 'purchases/purchase_list.html', {
        'purchases': purchases,
        'total_co2': total_co2,
        'total_amount': total_amount,
        'purchase_count': purchases.count()
    })


@login_required
def purchase_detail(request, pk):
    """Vue détaillée d'un achat."""
    purchase = get_object_or_404(PurchaseData, pk=pk, user=request.user)
    
    return render(request, 'purchases/purchase_detail.html', {
        'purchase': purchase
    })


@login_required
def purchase_delete(request, pk):
    """Suppression d'un achat."""
    purchase = get_object_or_404(PurchaseData, pk=pk, user=request.user)
    
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, '🗑️ Achat supprimé avec succès')
        return redirect('purchase_list')
    
    return render(request, 'purchases/purchase_confirm_delete.html', {
        'purchase': purchase
    })
