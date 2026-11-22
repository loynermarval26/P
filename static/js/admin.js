// AromaLuxe Admin Interactive Script

// 1-Click Stock Toggle via AJAX
async function toggleStock(perfumeId, btnElement) {
    btnElement.disabled = true;
    const originalText = btnElement.innerHTML;
    btnElement.innerHTML = `<span class="animate-spin inline-block">⏳</span>`;

    try {
        const response = await fetch(`/api/toggle-stock/${perfumeId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();

        if (result.success) {
            const inStock = result.data.in_stock === 1;
            const statusBadge = document.getElementById(`stock-badge-${perfumeId}`);
            
            if (statusBadge) {
                if (inStock) {
                    statusBadge.className = 'px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-500/30';
                    statusBadge.innerText = 'En Stock';
                } else {
                    statusBadge.className = 'px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-950/80 text-rose-400 border border-rose-500/30';
                    statusBadge.innerText = 'Agotado';
                }
            }

            // Update button appearance
            if (inStock) {
                btnElement.className = 'px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1 shadow-sm';
                btnElement.innerHTML = `✓ En Stock`;
            } else {
                btnElement.className = 'px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 transition flex items-center gap-1 shadow-sm';
                btnElement.innerHTML = `✕ Agotado`;
            }
        } else {
            alert('Error al cambiar stock: ' + (result.error || 'Desconocido'));
            btnElement.innerHTML = originalText;
        }
    } catch (err) {
        console.error(err);
        alert('Error de conexión al cambiar el stock.');
        btnElement.innerHTML = originalText;
    } finally {
        btnElement.disabled = false;
    }
}

// Image Preview Helper
function previewImage(input) {
    const previewContainer = document.getElementById('imagePreviewContainer');
    const previewImg = document.getElementById('imagePreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Accords Manager for perfume_form.html
class AccordsManager {
    constructor(containerId, hiddenInputId, initialAccords = []) {
        this.container = document.getElementById(containerId);
        this.hiddenInput = document.getElementById(hiddenInputId);
        this.accords = initialAccords;
        if (this.container && this.hiddenInput) {
            this.render();
        }
    }

    add(name, color, percent) {
        if (!name.trim()) return;
        this.accords.push({
            name: name.trim(),
            color: color || '#10B981',
            percent: parseInt(percent) || 75
        });
        this.render();
    }

    remove(index) {
        this.accords.splice(index, 1);
        this.render();
    }

    render() {
        if (!this.container) return;
        this.hiddenInput.value = JSON.stringify(this.accords);
        
        if (this.accords.length === 0) {
            this.container.innerHTML = `<p class="text-xs text-slate-500 italic">No hay acordes agregados. Añade los acordes olfativos abajo.</p>`;
            return;
        }

        let html = '<div class="space-y-2">';
        this.accords.forEach((acc, index) => {
            html += `
                <div class="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                    <div class="flex items-center gap-2 flex-1">
                        <span class="w-4 h-4 rounded-full border border-white/20" style="background-color: ${acc.color};"></span>
                        <span class="font-medium text-slate-200">${acc.name}</span>
                        <span class="text-slate-400">(${acc.percent}%)</span>
                    </div>
                    <div class="w-24 h-2 bg-slate-800 rounded-full overflow-hidden mr-3 hidden sm:block">
                        <div class="h-full rounded-full" style="width: ${acc.percent}%; background-color: ${acc.color};"></div>
                    </div>
                    <button type="button" onclick="window.accordsMgr.remove(${index})" class="text-rose-400 hover:text-rose-300 font-bold px-2 py-1">
                        ✕
                    </button>
                </div>
            `;
        });
        html += '</div>';
        this.container.innerHTML = html;
    }
}
