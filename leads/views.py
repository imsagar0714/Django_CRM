from django.core.mail import send_mail
from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
from .models import Lead,Agent,Category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .forms import Leadform, LeadModelForm,CustomUserCreationForm,AssignAgentForm,LeadCategoryUpdateForm
from agents.mixins import OrganiserAndLoginRequiredMixin



class Signupview(generic.CreateView):
    template_name="registration/signup.html"
    form_class=CustomUserCreationForm
    
    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name="landing.html"

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            # Organiser can see all leads in their organisation
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            # Agent can see only their own assigned leads
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                agent=user.agent
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            # Unassigned leads for organisers
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=True
            )
            context["unassigned_leads"] = queryset
        return context



class LeadDetailView(LoginRequiredMixin,generic.DetailView):
    template_name="leads/lead_detail.html"
    context_object_name="lead"
    
    def get_queryset(self):
        user=self.request.user
        #initial queryset of the leads for the entire organisation
        if user.is_organiser:
            queryset=Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset=Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset=queryset.filter(agent__user=user)
        return queryset
    
    
    
class LeadcreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name="leads/lead_create.html"
    form_class=LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation=self.request.user.userprofile
        lead.save()
        user = self.request.user
        if user.is_organiser:
            lead.organisation = user.userprofile   # organiser ka userprofile assign karo
        else:
            lead.organisation = user.agent.organisation  # agent ka organisation assign karo
        lead.save()
        return super(LeadcreateView, self).form_valid(form)
    
    
class LeadUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name="leads/lead_update.html"
    form_class=LeadModelForm
    
    def get_queryset(self):
        user=self.request.user
        #initial queryset of the leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)
    
    def get_success_url(self):
        return reverse("leads:lead-update",kwargs={'pk': self.object.pk})
    
class LeadDeleteView(OrganiserAndLoginRequiredMixin,generic.DeleteView):
    template_name="leads/lead_delete.html"
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def get_queryset(self):
        user=self.request.user
        #initial queryset of the leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)
    


class AssignAgentView(OrganiserAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm
    
    def get_form_kwargs(self):
        kwargs = super(AssignAgentView, self).get_form_kwargs()
        kwargs["request"] = self.request   # yaha request inject karo
        return kwargs
    
    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)

class CategoryListView(LoginRequiredMixin,generic.ListView):
    template_name="leads/category_list.html"
    context_object_name="category_list"
    def get_context_data(self, **kwargs):
        context=super(CategoryListView,self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
            )
        context.update({
            "unassigned_lead_count":Lead.objects.filter(category__isnull=True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset
    
class CategoryDetailView(LoginRequiredMixin,generic.DetailView):
    template_name="leads/category_detail.html"
    context_object_name="category"
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset
    
class LeadCategoryUpdateView(LoginRequiredMixin,generic.UpdateView):
    template_name="leads/lead_category_update.html"
    form_class=LeadCategoryUpdateForm
    
    def get_queryset(self):
        user=self.request.user
        #initial queryset of the leads for the entire organisation
        if user.is_organiser:
            queryset=Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset=Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset=queryset.filter(agent__user=user)
        return queryset
    
    def get_success_url(self):
        return reverse("leads:lead-detail",kwargs= { "pk" :  self.get_object().id})
    