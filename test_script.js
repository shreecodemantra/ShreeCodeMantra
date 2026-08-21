
        // Search and Filter functionality
        function applyFilters() {
            const searchTerm = document.getElementById('globalSearch').value;
            const categoryFilter = document.getElementById('categoryFilter').value;

            // Build URL with query parameters
            let url = new URL(window.location.href.split('?')[0]);
            let params = new URLSearchParams();

            if (searchTerm) params.set('search', searchTerm);
            if (categoryFilter) params.set('category', categoryFilter);

            window.location.href = url.pathname + '?' + params.toString();
        }

        // Enter key support for search
        document.getElementById('globalSearch').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });

        // View Project Details
        async function viewProject(projectId) {
            try {
                // Show loading
                Swal.fire({
                    title: 'Loading...',
                    text: 'Please wait while we fetch project details',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                const response = await fetch(`/admin/api/project/${projectId}`);
                const data = await response.json();

                Swal.close();

                if (data.success) {
                    const project = data.project;

                    Swal.fire({
                        title: `<span class="text-xl font-bold">${project.title}</span>`,
                        html: `
                            <div class="text-left max-h-96 overflow-y-auto">
                                ${project.files && project.files.main_image ?
                                `<img src="/static/${project.files.main_image}" alt="${project.title}" 
                                          class="w-full h-48 object-cover rounded-lg mb-4"
                                          onerror="this.style.display='none'">` :
                                '<div class="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center mb-4">' +
                                '<i class="fas fa-image text-gray-400 text-4xl"></i></div>'
                            }
                                <div class="space-y-3">
                                    <div>
                                        <strong class="text-gray-700">Description:</strong>
                                        <p class="text-gray-600 mt-1">${project.description || 'No description available'}</p>
                                    </div>
                                    <div>
                                        <strong class="text-gray-700">Category:</strong>
                                        <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">${project.category || 'Uncategorized'}</span>
                                    </div>
                                    <div>
                                        <strong class="text-gray-700">Price:</strong>
                                        <span class="ml-2 text-green-600 font-semibold">$${project.price || 0}</span>
                                    </div>
                                    <div>
                                        <strong class="text-gray-700">Tech Stack:</strong>
                                        <div class="flex flex-wrap gap-1 mt-1">
                                            ${(project.tech_stack && project.tech_stack.length > 0) ?
                                project.tech_stack.map(tech =>
                                    `<span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">${tech}</span>`
                                ).join('') :
                                '<span class="text-gray-500 text-sm">No technologies specified</span>'
                            }
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4 text-sm text-gray-500">
                                        <div>
                                            <strong>Upload Date:</strong>
                                            <p>${project.upload_date || 'Unknown'}</p>
                                        </div>
                                        ${project.updated_date ? `
                                        <div>
                                            <strong>Last Updated:</strong>
                                            <p>${project.updated_date}</p>
                                        </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `,
                        width: '700px',
                        showCloseButton: true,
                        showConfirmButton: false,
                        customClass: {
                            popup: 'rounded-lg'
                        }
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.message || 'Failed to load project details',
                        icon: 'error',
                        confirmButtonColor: '#3b82f6'
                    });
                }
            } catch (error) {
                Swal.close();
                Swal.fire({
                    title: 'Error',
                    text: 'Failed to load project details',
                    icon: 'error',
                    confirmButtonColor: '#3b82f6'
                });
            }
        }

        // Edit Project - Redirect to edit page
        function editProject(projectId) {
            window.location.href = `/admin/project/edit/${projectId}`;
        }

        // Delete Project with confirmation
        async function deleteProject(projectId) {
            const result = await Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#6b7280',
                confirmButtonText: 'Yes, delete it!',
                cancelButtonText: 'Cancel'
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch(`/admin/project/delete/${projectId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        Swal.fire({
                            title: 'Deleted!',
                            text: data.message,
                            icon: 'success',
                            confirmButtonColor: '#3b82f6'
                        }).then(() => {
                            // Reload the page to reflect changes
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            title: 'Error!',
                            text: data.message,
                            icon: 'error',
                            confirmButtonColor: '#3b82f6'
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to delete project',
                        icon: 'error',
                        confirmButtonColor: '#3b82f6'
                    });
                }
            }
        }

    